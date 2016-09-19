import requests

from pyramid import security

from lovely.pyrest.rest import RestService, rpcmethod_route, rpcmethod_view

from iris.service.rest.swagger import swagger_reduce_response

from ..endpoint import EndpointErrorMixin

from .og import og_data_for_url


@RestService("ogcheck")
class OGCheckServiceAPI(EndpointErrorMixin):

    def __init__(self, request):
        self.request = request

    @rpcmethod_route(request_method='POST')
    @rpcmethod_view(http_cache=0,
                    permission=security.NO_PERMISSION_REQUIRED)
    @swagger_reduce_response
    def check(self, url):
        try:
            data = og_data_for_url(url)
        except requests.exceptions.RequestException:
            raise self.bad_request(replacements={'message': 'og_check_failed'})
        return {
            "data": data,
            "status": "ok"
        }
