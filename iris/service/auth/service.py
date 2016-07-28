from lovely.pyrest.rest import RestService, rpcmethod_route, rpcmethod_view

from iris.service.rest.swagger import swagger_reduce_response

from ..endpoint import EndpointErrorMixin, BadRequest
from ..errors import Errors

from .ssotoken import SSOToken
from .secret import verify_message
from .security import login_user, logout_user
from .sso import get_or_create_sso_user


@RestService("auth_api")
class AuthService(EndpointErrorMixin):

    def __init__(self, request):
        self.request = request

    @rpcmethod_route(request_method='OPTIONS',
                     route_suffix='/whoami')
    @rpcmethod_view(http_cache=0)
    def whoamiOptions(self, **kwargs):
        return {}

    @rpcmethod_route(request_method='GET',
                     route_suffix='/whoami')
    @rpcmethod_view(http_cache=0)
    @swagger_reduce_response
    def whoami(self, **kwargs):
        try:
            self.request.user = self._ssouser(False)
        except BadRequest as e:
            if e.message != Errors.no_parameters:
                raise
        return self._whoami()

    def _whoami(self):
        user = self.request.user
        if user is None:
            raise self.bad_request(Errors.not_logged_in)
        return {'data': user.get_source()}

    @rpcmethod_route(request_method='OPTIONS',
                     route_suffix='/ssologin')
    @rpcmethod_view(http_cache=0)
    def ssologinOptions(self, **kwargs):
        return {}

    @rpcmethod_route(request_method='POST',
                     route_suffix='/ssologin')
    @rpcmethod_view(http_cache=0)
    @swagger_reduce_response
    def ssologin(self, **kwargs):
        user = self._ssouser(allow_no_params=False)
        if user is not None:
            login_user(self.request, self.request.response, user)
        return self._whoami()

    def _ssouser(self, allow_no_params):
        data = self.request.swagger_data
        sso = data.get('sso')
        token = data.get('token')
        if (sso is None) == (token is None):
            # at least one of 'sso' or 'token' must be provided but not
            # both together.
            if sso is None:
                if allow_no_params:
                    return None
                raise self.bad_request(Errors.no_parameters)
            raise self.bad_request(Errors.too_many_parameters)
        ssodata = self.request.sso_data()
        if ssodata is None:
            return None
        # With sso data we can get the sso user and login
        return get_or_create_sso_user(ssodata)

    @rpcmethod_route(request_method='OPTIONS',
                     route_suffix='/ssotoken')
    @rpcmethod_view(http_cache=0)
    def ssotokenOptions(self, **kwargs):
        return {}

    @rpcmethod_route(request_method='POST',
                     route_suffix='/ssotoken')
    @rpcmethod_view(http_cache=0)
    def ssotoken(self, **kwargs):
        data = self.request.swagger_data
        sso = data['sso']
        apikey = data['apikey']
        try:
            verify_message(sso, apikey)
        except ValueError:
            raise self.bad_request(Errors.sso_invalid_data)
        except KeyError:
            raise self.bad_request(Errors.sso_unknown_api_key)
        token = SSOToken(sso=sso, apikey=apikey)
        token.store(refresh=True)
        return {
            "token": token.token
        }

    @rpcmethod_route(request_method='OPTIONS',
                     route_suffix='/logout')
    @rpcmethod_view(http_cache=0)
    def logoutOptions(self, **kwargs):
        return {}

    @rpcmethod_route(request_method='POST',
                     route_suffix='/logout')
    @rpcmethod_view(http_cache=0)
    def logout(self, **kwargs):
        logout_user(self.request, self.request.response)
        return {}
