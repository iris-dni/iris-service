from pyramid.httpexceptions import HTTPFound

from pyramid.view import view_config

from .security import login_user, logout_user
from .sso import get_or_create_sso_user


@view_config(route_name='login_embed',
             request_method='GET',
             renderer='templates/login_embed.jinja2'
            )
def login_embed(request):
    request.response.content_type = 'application/javascript'
    return {
        'apiBasePath': request.application_url,
        'redirectUrl': request.route_url('sso_login_redirect'),
    }


@view_config(route_name='sso_login_redirect',
             request_method='GET',
            )
def sso_login_redirect(request):
    loggedIn = False
    data = request.GET
    #TODO: get a default redirect
    redirecturl = data.get('redirecturl')
    response = HTTPFound(redirecturl)
    token = data.get('token')
    if token:
        request.swagger_data = {
            'token': token,
            'irisreturl': redirecturl,
        }
        ssodata = request.sso_data()
        if ssodata is not None:
            # With sso data we can get the sso user and login
            user = get_or_create_sso_user(ssodata)
            if user is not None:
                login_user(request, response, user)
                loggedIn = True
    if not loggedIn:
        # make sure we are logged out
        logout_user(request, response)
    return response
