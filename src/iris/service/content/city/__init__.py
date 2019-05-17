from . import service  # noqa
from .document import City  # noqa
from . import document


def includeme(config):
    settings = config.get_settings()
    document.DEFAULT_TRESHOLD = int(settings.get('iris.city.treshold', 0))
    from iris.service.rest import auth
    config.add_route('city_public_api',
                     'cities',
                     static=True,
                    )
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
