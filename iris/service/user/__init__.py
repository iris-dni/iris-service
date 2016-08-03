from . import service  # noqa
from .document import User  # noqa


def includeme(config):
    from iris.service.rest import admin
    config.add_route('user_admin_api',
                     'admin/users',
                     static=True,
                     factory=admin.AdminServiceAuthFactory,
                    )
