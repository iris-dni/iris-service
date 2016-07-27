from . import service  # noqa
from .ssotoken import SSOToken  # noqa


def includeme(config):
    config.add_route('auth_api',
                     'auth',
                     static=True)
