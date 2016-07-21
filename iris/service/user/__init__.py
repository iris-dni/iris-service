from . import service  # noqa
from .document import User  # noqa


def includeme(config):
    config.add_route('user_admin_api',
                     'admin/users',
                     static=True)
