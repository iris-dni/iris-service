from pyramid import security

from lovely.pyrest.rest import RestService, rpcmethod_route, rpcmethod_view

from iris.service import rest
from iris.service.rest.swagger import swagger_reduce_response


@RestService("statemachine_api")
class StatemachineRESTService(rest.BaseRESTService):
    """A generic endpoint to provide statemachine data

    The request is forwarded to a mapper which must provide a `statemachine`
    method.
    """

    @rpcmethod_route(request_method='OPTIONS',
                     route_suffix='/{name}')
    @rpcmethod_view(http_cache=0,
                    permission=security.NO_PERMISSION_REQUIRED)
    def options_contentId_support(self, **kwargs):
        data = self.request.swagger_data
        self._getMapper(data['name'], 'statemachine')
        return {}

    @rpcmethod_route(request_method='GET',
                     route_suffix='/{name}')
    @swagger_reduce_response
    def statemachine(self, **kwargs):
        data = self.request.swagger_data
        mapper = self._getMapper(data['name'], 'statemachine')
        return {
            "data": mapper.statemachine()
        }
