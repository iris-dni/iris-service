from . import service  # noqa
from .ssotoken import SSOToken  # noqa
from . import views  # noqa


def includeme(config):
    config.add_route('auth_api',
                     'auth',
                     static=True)
    config.add_route('login_embed',
                     'views/iris-sso-login.js')
