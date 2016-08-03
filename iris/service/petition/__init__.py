from . import service  # noqa
from .document import Petition  # noqa


def includeme(config):
    from iris.service.rest import admin
    config.add_route('petition_admin_api',
                     'admin/petitions',
                     static=True,
                     factory=admin.AdminServiceAuthFactory,
                    )
    config.add_route('petition_public_api',
                     'petitions',
                     static=True)
