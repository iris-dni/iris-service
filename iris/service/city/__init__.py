from . import service  # noqa
from .document import City  # noqa


def includeme(config):
    from iris.service.rest import auth
    config.add_route('city_admin_api',
                     'admin/cities',
                     static=True,
                     factory=auth.AdminServiceAuthFactory,
                    )
    config.add_route('city_import_api',
                     'import/cities',
                     static=True,
                     factory=auth.ApiKeyServiceAuthFactory,
                    )
