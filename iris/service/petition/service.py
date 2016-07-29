from lovely.pyrest.rest import RestService, rpcmethod_route, rpcmethod_view

from iris.service import rest
from iris.service.rest import queries

from ..errors import Errors

from .sm import PetitionStateMachine
from .document import Petition


@RestService("petition_admin_api")
class PetitionAdminRESTService(rest.RESTService):

    MAPPER_NAME = 'petitions'


class PetitionsRESTMapper(rest.DocumentRESTMapperMixin,
                          rest.SearchableDocumentRESTMapperMixin,
                          rest.RESTMapper):
    """A mapper for the petitions admin REST API
    """

    NAME = 'petitions'

    DOC_CLASS = Petition

    QUERY_PARAMS = {
        'state': queries.termsFilter('state'),
        'tags': queries.termsFilter('tags'),
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

    SORT_PARAMS = {
        'created': queries.fieldSorter('dc.created'),
        'modified': queries.fieldSorter('dc.modified'),
        'id': queries.fieldSorter('id'),
        'state': queries.fieldSorter('state'),
        'supporters.amount': queries.fieldSorter('supporters.amount'),
        'score': queries.scoreSorter,
        'default': queries.fieldSorter('dc.created', 'DESC'),
    }

    def support(self, contentId, data):
        """Sign a petition
        """
        petition = Petition.get(contentId)
        if petition is None:
            return None
        # TODO: support the petition
        return {}

    def event(self, contentId, transitionName, data=None):
        petition = Petition.get(contentId)
        if petition is None:
            return None
        # TODO: implement event state handling
        sm = PetitionStateMachine(petition)
        state = sm.switch(transitionName)
        if state:
            petition.state = state
            petition.store(refresh=True)
        return self.doc_as_dict(petition)


@RestService("petition_public_api")
class PetitionPublicRESTService(rest.RESTService):
    """Public petition endpoint

    We reuse the BaseRESTService for the simple endpoints.
    """

    MAPPER_NAME = 'petitions'

    @rpcmethod_route(request_method='OPTIONS',
                     route_suffix='/{contentId}/support')
    @rpcmethod_view(http_cache=0)
    def options_contentId_support(self, **kwargs):
        return {}

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}/support')
    def support(self, **kwargs):
        mapper = self._getMapper(self.MAPPER_NAME)
        result = mapper.support(**self.request.swagger_data)
        if result is None:
            raise self.not_found(
                Errors.document_not_found,
                {
                    'contentId': self.request.swagger_data.get('contentId',
                                                               'missing'),
                    'mapperName': self.MAPPER_NAME
                }
            )
        return result

    @rpcmethod_route(request_method='OPTIONS',
                     route_suffix='/{contentId}/event/{transitionName}')
    @rpcmethod_view(http_cache=0)
    def options_contentId_event(self, **kwargs):
        return {}

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}/event/reject')
    def event_reject(self, **kwargs):
        return self._event('reject')

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}/event/publish')
    def event_publish(self, **kwargs):
        return self._event('publish')

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}/event/delete')
    def event_delete(self, **kwargs):
        return self._event('delete')

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}/event/close')
    def event_close(self, **kwargs):
        return self._event('close')

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}/event/approved')
    def event_approved(self, **kwargs):
        return self._event('approved')

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}/event/sendLetter')
    def event_sendLetter(self, **kwargs):
        return self._event('sendLetter')

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}/event/setFeedback')
    def event_setFeedback(self, **kwargs):
        return self._event('setFeedback')

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}/event/{transitionName}')
    def event_generic(self, **kwargs):
        switch = self.request.swagger_data.pop('transitionName')
        return self._event(switch)

    def _event(self, switch):
        mapper = self._getMapper(self.MAPPER_NAME)
        result = mapper.event(transitionName=switch,
                              **self.request.swagger_data)
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
