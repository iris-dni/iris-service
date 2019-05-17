from pyramid import security

from lovely.pyrest.rest import RestService, rpcmethod_route, rpcmethod_view

from iris.service.rest.swagger import swagger_reduce_response
from iris.service.security.security import login_user, logout_user

from iris.service.content.user import SessionUser

from ..endpoint import EndpointErrorMixin, BadRequest
from ..errors import Errors

from .ssotoken import SSOToken
from .sso import get_or_create_sso_user, verify_message


@RestService("auth_api")
class AuthService(EndpointErrorMixin):

    def __init__(self, request):
        self.request = request

    @rpcmethod_route(request_method='OPTIONS',
                     route_suffix='/whoami')
    @rpcmethod_view(http_cache=0,
                    permission=security.NO_PERMISSION_REQUIRED)
    def whoamiOptions(self, **kwargs):
        return {}

    @rpcmethod_route(request_method='GET',
                     route_suffix='/whoami')
    @rpcmethod_view(http_cache=0)
    @swagger_reduce_response
    def whoami(self, **kwargs):
        try:
            self.request.user = self._ssouser(allow_token_login=True)
        except BadRequest as e:
            if e.error_code != Errors.no_parameters:
                raise
        return self._whoami()

    def _whoami(self):
        user = self.request.user
        authenticated = (user is not None
                         and not SessionUser.is_session_user(user)
                        )
        result = {
            'status': authenticated and 'ok' or 'unauthenticated'
        }
        if authenticated:
            result['data'] = user.get_source()
        return result

    @rpcmethod_route(request_method='OPTIONS',
                     route_suffix='/ssologin')
    @rpcmethod_view(http_cache=0,
                    permission=security.NO_PERMISSION_REQUIRED)
    def ssologinOptions(self, **kwargs):
        return {}

    @rpcmethod_route(request_method='POST',
                     route_suffix='/ssologin')
    @rpcmethod_view(http_cache=0)
    @swagger_reduce_response
    def ssologin(self, **kwargs):
        self._ssouser(allow_login=True)
        return self._whoami()

    def _ssouser(self, allow_login=False, allow_token_login=False):
        """Get the sso user from sso data

        Data can be provided as sso/apikey combination or as token.

        If the sso data is empty or contains no email ('{}') a logout is
        performed on self.request.response.

        allow_login=True will also login the user
        allow_token_login=True will login the user if there was a token used
        """
        data = self.request.swagger_data
        sso = data.get('sso')
        token = data.get('token')
        if (sso is None) == (token is None):
            # at least one of 'sso' or 'token' must be provided but not
            # both together.
            if sso is None:
                raise self.bad_request(Errors.no_parameters)
            raise self.bad_request(Errors.too_many_parameters)
        ssodata = self.request.sso_data()
        if ssodata is None:
            logout_user(self.request, self.request.response)
            return None
        # With sso data we can get the sso user and login
        user = get_or_create_sso_user(ssodata)
        if (user is not None
            and (allow_login
                 or (token is not None and allow_token_login)
                )
           ):
            login_user(self.request, self.request.response, user)
        else:
            logout_user(self.request, self.request.response)
        return user

    @rpcmethod_route(request_method='OPTIONS',
                     route_suffix='/ssotoken')
    @rpcmethod_view(http_cache=0,
                    permission=security.NO_PERMISSION_REQUIRED)
    def ssotokenOptions(self, **kwargs):
        return {}

    @rpcmethod_route(request_method='POST',
                     route_suffix='/ssotoken')
    @rpcmethod_view(http_cache=0)
    @swagger_reduce_response
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
    @rpcmethod_view(http_cache=0,
                    permission=security.NO_PERMISSION_REQUIRED)
    def logoutOptions(self, **kwargs):
        return {}

    @rpcmethod_route(request_method='POST',
                     route_suffix='/logout')
    @rpcmethod_view(http_cache=0)
    @swagger_reduce_response
    def logout(self, **kwargs):
        logout_user(self.request, self.request.response)
        return {}
