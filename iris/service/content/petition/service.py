import transitions

from transitions.extensions.nesting import NestedState

from pyramid import security

from lovely.pyrest.rest import RestService, rpcmethod_route, rpcmethod_view

from iris.service import rest
from iris.service.rest import queries
from iris.service.security import acl

from iris.service.errors import Errors
from iris.service.rest.swagger import swagger_reduce_response
from iris.service.rest.extender import APIExtender

from iris.service.content.user import SessionUser

from .sm import PetitionStateMachine, fromYAML, ConditionError
from .document import Petition, Supporter


PETITIONS_MAPPER_NAME = 'petitions'


@RestService("petition_admin_api",
             permission=acl.Permissions.AdminFull)
class PetitionAdminRESTService(rest.RESTService):

    MAPPER_NAME = PETITIONS_MAPPER_NAME


def stateFilter(value):
    if isinstance(value, (list, tuple)):
        states = [v.strip() for v in value if v.strip()]
    else:
        states = [v.lower().strip() for v in value.split(',') if v.strip()]
    if not states:
        raise ValueError("No states provided")
    filters = []
    for state in states:
        parts = state.split(NestedState.separator, 1)
        if len(parts) > 1:
            parent, name = parts
            if not name or name == '*':
                filters.append(queries.termFilter('state.parent')(parent))
            else:
                filters.append({
                    "bool": {
                        "must": [
                            queries.termFilter('state.name')(name),
                            queries.termFilter('state.parent')(parent)
                        ]
                    }
                })
        else:
            filters.append(queries.termFilter('state.name')(parts[0]))
    if len(filters) == 1:
        return filters[0]
    return {
        "bool": {
            "should": filters
        }
    }


class PetitionsRESTMapper(rest.DocumentRESTMapperMixin,
                          rest.SearchableDocumentRESTMapperMixin,
                          rest.RESTMapper):
    """A mapper for the petitions admin REST API
    """

    NAME = 'petitions'

    DOC_CLASS = Petition

    QUERY_PARAMS = {
        'ft': queries.fulltextQuery(['tags_ft',
                                     'title_ft',
                                     'description_ft',
                                     'suggested_solution_ft',
                                    ]),
        'tags_ft': queries.fulltextQuery(['tags_ft']),
        'title_ft': queries.fulltextQuery(['title_ft']),
        'description_ft': queries.fulltextQuery(['description_ft']),
        'suggested_solution_ft': queries.fulltextQuery(
            ['suggested_solution_ft']
        ),
    }

    FILTER_PARAMS = {
        'state': stateFilter,
        'tags': queries.termsFilter('tags'),
        'city': queries.termsFilter('relations.city'),
        'owner': queries.termsFilter('relations.owner.id'),
    }

    SORT_PARAMS = {
        'created': queries.fieldSorter('dc.created'),
        'modified': queries.fieldSorter('dc.modified'),
        'id': queries.fieldSorter('id'),
        'state': queries.fieldSorter('state.name'),
        'state.parent': queries.fieldSorter('state.parent'),
        'supporters.amount': queries.fieldSorter('supporters.amount'),
        'score': queries.scoreSorter,
        'default': queries.fieldSorter('dc.created', 'DESC'),
    }

    def event(self, contentId, transitionName, data={},
              resolve=[], extend=[]):
        petition = Petition.get(contentId)
        if petition is None:
            return None
        sm = PetitionStateMachine(petition, self.request)
        transition_fn = getattr(sm, transitionName)
        if transition_fn is None:
            # transition doesn't exist
            raise transitions.MachineError(
                'Unknown transition "%s"' % transitionName)
        done = transition_fn(**data)
        if done:
            petition.store(refresh=True)
        return self.to_api(petition, resolve, extend)

    def statemachine(self):
        return fromYAML(raw=True)

    def get_by_token(self, token, resolve=[], extend=[]):
        doc = None
        found = self.DOC_CLASS.get_by(Petition.response_token, token)
        if found:
            doc = found[0]
        return self.to_api(doc, resolve, extend)

    def _prepare_data(self, doc, data):
        """Prepare API POST data for a petition

        The owner of the petition is set based on the current user from the
        request. This can also be a session user. An already set owner will be
        changed.
        """
        data_owner = data.get('owner', {})
        if doc is None:
            # New document, set the owner id to the currently logged in user
            owner = data.setdefault('owner', {})
            owner['id'] = self.request.session_user.id
        elif (data_owner.get('id') is None
              and (doc.owner.id is None
                   or SessionUser.is_session_user_id(doc.owner.id)
                  )
             ):
            # Existing document and no owner or owner is a session user.
            # Force the owner to the currently logged in user.
            doc.owner = self.request.session_user.id
        # manage the trusted flags if this is a change of an existing petition
        if doc is not None:
            # Check if the trusted flags on the relations are different
            # and reset the trusted flag is so.
            owner_rel = doc.owner.relation_dict
            if owner_rel.get('mobile') != data_owner.get('mobile'):
                data_owner['mobile_trusted'] = False
            if owner_rel.get('email') != data_owner.get('email'):
                data_owner['email_trusted'] = False

    def _prepare_document(self, doc, data, is_create):
        """Prepare the document before it is stored

        Manage the trusted flags.
        """
        owner = doc.owner()
        if owner is None:
            # No owner or a session owner, flags are already set in
            # _prepare_data.
            return
        owner_rel = doc.owner.relation_dict
        if (owner_rel['mobile'] == owner.mobile
            and owner.mobile_trusted
           ):
            # The owners mobile is trusted so we can also trust the mobile
            # on the relation.
            doc.owner = {'mobile_trusted': True}
        if (owner_rel['email'] == owner.email
            and owner.email_trusted
           ):
            # The owners email is trusted so we can also trust the email
            # on the relation.
            doc.owner = {'email_trusted': True}


@RestService("petition_public_api")
class PetitionPublicRESTService(rest.RESTService):
    """Public petition endpoint

    We reuse the RESTService for the simple endpoints.

    The REST methods from the base class which should not be available must
    not be configured in swagger.
    """

    MAPPER_NAME = PETITIONS_MAPPER_NAME

    @rpcmethod_route(request_method='OPTIONS',
                     route_suffix='/{contentId}/event/{transitionName}')
    @rpcmethod_view(http_cache=0,
                    permission=security.NO_PERMISSION_REQUIRED)
    def options_event_generic(self, **kwargs):
        return {}

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}/event/reject')
    @swagger_reduce_response
    def event_reject(self, **kwargs):
        return self._event('reject')

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}/event/publish')
    @swagger_reduce_response
    def event_publish(self, **kwargs):
        return self._event('publish')

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}/event/delete')
    @swagger_reduce_response
    def event_delete(self, **kwargs):
        return self._event('delete')

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}/event/support')
    @swagger_reduce_response
    def event_support(self, **kwargs):
        return self._event('support')

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}/event/close')
    @swagger_reduce_response
    def event_close(self, **kwargs):
        return self._event('close')

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}/event/approved')
    @swagger_reduce_response
    def event_approved(self, **kwargs):
        return self._event('approved')

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}/event/letterSent')
    @swagger_reduce_response
    def event_letterSent(self, **kwargs):
        return self._event('letterSent')

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}/event/setFeedback')
    @swagger_reduce_response
    def event_setFeedback(self, **kwargs):
        token = self.request.swagger_data['data']['data']['token']
        contentId = self.request.swagger_data['contentId']
        petition = Petition.get(contentId)
        if petition is not None and petition.response_token != token:
            raise self.bad_request(Errors.wrong_token)
        return self._event('setFeedback')

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}/event/check')
    @swagger_reduce_response
    def event_check(self, **kwargs):
        return self._event('check')

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}/event/tick')
    @swagger_reduce_response
    def event_tick(self, **kwargs):
        return self._event('tick')

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}/event/force_state')
    @rpcmethod_view(http_cache=0,
                    permission=acl.Permissions.AdminFull)
    @swagger_reduce_response
    def event_force_state(self, **kwargs):
        return self._event('force_state')

    def _event(self, switch):
        mapper = self._getMapper(self.MAPPER_NAME)
        try:
            result = mapper.event(transitionName=switch,
                                  **self.request.swagger_data)
        except transitions.MachineError as e:
            raise self.bad_request(Errors.sm_transition_error,
                                   replacements={
                                       'text': e.value
                                   })
        if result is None:
            raise self.not_found(
                Errors.document_not_found,
                {
                    'contentId': self.request.swagger_data.get('contentId',
                                                               'missing'),
                    'mapperName': self.MAPPER_NAME
                }
            )
        return {"data": result, "status": "ok"}


@RestService("supporter_admin_api",
             permission=acl.Permissions.AdminFull)
class SupportersAdminRESTService(rest.RESTService):

    MAPPER_NAME = 'supporters'


class SupportersRESTMapper(rest.DocumentRESTMapperMixin,
                           rest.SearchableDocumentRESTMapperMixin,
                           rest.RESTMapper):
    """A mapper for the supporters admin REST API
    """

    NAME = 'supporters'

    DOC_CLASS = Supporter

    QUERY_PARAMS = {
    }

    FILTER_PARAMS = {
        'petition': queries.termsFilter('relations.petition'),
        'user': queries.termsFilter('relations.user'),
    }

    SORT_PARAMS = {
        'created': queries.fieldSorter('dc.created'),
        'id': queries.fieldSorter('id'),
        'default': queries.fieldSorter('dc.created', 'DESC'),
    }


@RestService("petition_by_token_api")
class PetitionByTokenRESTService(rest.BaseRESTService):
    """Public petition endpoint to get a petition by token
    """

    MAPPER_NAME = PETITIONS_MAPPER_NAME

    @rpcmethod_route(request_method='OPTIONS',
                     route_suffix='/{token}/petitions')
    @rpcmethod_view(http_cache=0)
    def options(self, **kwargs):
        return {}

    @rpcmethod_route(request_method='GET',
                     route_suffix='/{token}/petitions')
    @rpcmethod_view(http_cache=0,
                    permission=security.NO_PERMISSION_REQUIRED)
    @swagger_reduce_response
    def get_petition_by_token(self, **kwargs):
        return self.get_content(self.MAPPER_NAME,
                                **self.request.swagger_data)

    def get_content(self, mapperName, token, resolve=[], extend=[]):
        mapper = self._getMapper(mapperName)
        try:
            data = mapper.get_by_token(token, resolve, extend)
        except NotImplementedError as e:
            raise self.method_not_allowed(replacements={'message': e.message})
        if data is None:
            raise self.not_found(Errors.token_not_found,
                                 {'token': token,
                                  'mapperName': mapperName
                                 }
                                )
        return {"data": data}


class SupportingExtender(object):
    """Extends a petition with the flag "supporting"

    "supporting" is true if the currently logged in user already supports a
    petition.
    If no user is logged in "supporting" is set to false.
    """

    NAME = 'supporting'

    def __init__(self, request, docs):
        self.request = request
        self.docs = docs

    def extend(self, docs):
        if not isinstance(docs, list):
            docs = [docs]
        user = self.request.user
        if user is None:
            for doc in docs:
                APIExtender.applyExtensionData(doc, self.NAME, False)
            return
        query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "terms": {
                                "relations.petition": [d.id
                                                       for d in self.docs
                                                       if d]
                            }
                        },
                        {
                            "term": {
                                "relations.user": user.id
                            }
                        },
                    ]
                }
            }
        }
        supporters = Supporter.search(query)
        supporters = {d.petition.id: d for d in supporters['hits']['hits']}
        for doc in docs:
            if doc is None:
                continue
            supporting = doc.get('id') in supporters
            APIExtender.applyExtensionData(doc, self.NAME, supporting)

APIExtender.register(SupportingExtender.NAME, SupportingExtender)
