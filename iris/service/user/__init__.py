from . import service  # noqa
from .document import User  # noqa


def includeme(config):
    from iris.service.rest import auth
    config.add_route('user_admin_api',
                     'admin/users',
                     static=True,
                     factory=auth.AdminServiceAuthFactory,
                    )
