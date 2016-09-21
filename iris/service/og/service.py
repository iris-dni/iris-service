import time
import requests

from pyramid import security

from lovely.pyrest.rest import RestService, rpcmethod_route, rpcmethod_view

from iris.service.rest.swagger import swagger_reduce_response
from iris.service.content.weblocation import WebLocation

from ..endpoint import EndpointErrorMixin

from .og import og_data_for_url, normalize_url


@RestService("ogcheck")
class OGCheckServiceAPI(EndpointErrorMixin):

    def __init__(self, request):
        self.request = request

    @rpcmethod_route(request_method='POST')
    @rpcmethod_view(http_cache=0,
                    permission=security.NO_PERMISSION_REQUIRED)
    @swagger_reduce_response
    def check(self, url):
        url = normalize_url(url)
        urls = WebLocation.mget_urls([url])
        if urls and urls[0] is not None:
            data = urls[0].og
        else:
            try:
                data = og_data_for_url(url)
            except requests.exceptions.RequestException:
                raise self.bad_request(
                    replacements={'message': 'og_check_failed'})
            if data is not None:
                loc = WebLocation(url=url)
                loc.og = dict(**data)
                loc.og['ts'] = int(time.time() * 1000)
                loc.store()
        return {
            "data": data,
            "status": "ok"
        }
