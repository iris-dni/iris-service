from lovely.pyrest.rest import RestService, rpcmethod_route, rpcmethod_view

from iris.service import rest

from ..errors import Errors

from .document import Petition


class PetitionsRESTMapper(rest.DocumentRESTMapperMixin, rest.RESTMapper):
    """A mapper for the petitions admin REST API
    """

    NAME = 'petitions'

    DOC_CLASS = Petition

    def sign(self, contentId, data):
        """Sign a petition
        """
        petition = Petition.get(contentId)
        if petition is None:
            return None
        # TODO: sign the petition
        return {}


@RestService("petition_public_api")
class PetitionPublicRESTService(rest.BaseRESTService):
    """Public petition endpoint

    We reuse the BaseRESTService for the simple endpoints.
    """

    MAPPER_NAME = 'petitions'

    @rpcmethod_route(route_suffix='/{contentId}')
    @rpcmethod_view(http_cache=0)
    def get(self, **kwargs):
        return self.get_content(self.MAPPER_NAME, **self.request.swagger_data)

    @rpcmethod_route(request_method='POST')
    def create(self, data, **kwargs):
        return self.create_content(self.MAPPER_NAME, **self.request.swagger_data)

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}')
    def update(self, contentId, data, **kwargs):
        return self.update_content(self.MAPPER_NAME, contentId, data)

    @rpcmethod_route(request_method='DELETE',
                     route_suffix='/{contentId}')
    def delete(self, contentId, **kwargs):
        return self.delete_content(self.MAPPER_NAME, contentId)

    @rpcmethod_route()
    @rpcmethod_view(http_cache=0)
    def search(self, **kwargs):
        return self.search_content(self.MAPPER_NAME)

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}/sign')
    def sign(self, contentId, data, **kwargs):
        mapper = self._getMapper(self.MAPPER_NAME)
        result = mapper.sign(contentId, data)
        if result is None:
            raise self.not_found(Errors.document_not_found,
                                 {'contentId': contentId,
                                  'mapperName': self.MAPPER_NAME
                                 }
                                )
        return result
