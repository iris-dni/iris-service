from . import service  # noqa
from .document import City  # noqa


def includeme(config):
    from iris.service.rest import admin
    config.add_route('city_admin_api',
                     'admin/cities',
                     static=True,
                     factory=admin.AdminServiceAuthFactory,
                    )
