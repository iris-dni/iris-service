from lovely.pyrest.rest import RestService, rpcmethod_route, rpcmethod_view

from iris.service import rest

from ..errors import Errors

from .document import Petition


@RestService("petition_admin_api")
class PetitionAdminRESTService(rest.RESTService):

    MAPPER_NAME = 'petitions'


class PetitionsRESTMapper(rest.DocumentRESTMapperMixin, rest.RESTMapper):
    """A mapper for the petitions admin REST API
    """

    NAME = 'petitions'

    DOC_CLASS = Petition

    def support(self, contentId, data):
        """Sign a petition
        """
        petition = Petition.get(contentId)
        if petition is None:
            return None
        # TODO: support the petition
        return {}

    def state(self, contentId, transitionName, data=None):
        petition = Petition.get(contentId)
        if petition is None:
            return None
        # TODO: implement state handling
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
                     route_suffix='/{contentId}/state({transitionName}')
    @rpcmethod_view(http_cache=0)
    def options_contentId_state(self, **kwargs):
        return {}

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}/state/reject')
    def state_reject(self, **kwargs):
        return self._state()

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}/state/{transitionName}')
    def state(self, **kwargs):
        return self._state()

    def _state(self):
        mapper = self._getMapper(self.MAPPER_NAME)
        result = mapper.state(**self.request.swagger_data)
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
