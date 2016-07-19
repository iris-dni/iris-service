from . import service  # noqa
from .document import Petition  # noqa


def includeme(config):
    config.add_route('petition_admin_api',
                     'admin/petitions',
                     static=True)
    config.add_route('petition_public_api',
                     'petitions',
                     static=True)
