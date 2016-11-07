import transitions

from pyramid import security

from lovely.pyrest.rest import RestService, rpcmethod_route, rpcmethod_view

from iris.service import rest
from iris.service.security import acl

from iris.service.errors import Errors
from iris.service.rest.swagger import swagger_reduce_response
from iris.service.rest.extender import APIExtender

from .document import Petition, Supporter
from .mapper import PETITIONS_MAPPER_NAME


@RestService("petition_admin_api",
             permission=acl.Permissions.AdminFull)
class PetitionAdminRESTService(rest.RESTService):

    MAPPER_NAME = PETITIONS_MAPPER_NAME


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
        except (KeyError, ValueError) as e:
            raise self.bad_request(replacements={'message': e.message})
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
                                "relations.user.id": user.id
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
