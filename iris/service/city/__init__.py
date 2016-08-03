from . import service  # noqa
from .document import City  # noqa


def includeme(config):
    config.add_route('city_admin_api',
                     'admin/cities',
                     static=True)
