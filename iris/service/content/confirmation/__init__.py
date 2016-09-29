from . import service  # noqa
from . import handler  # noqa
from .document import Confirmation  # noqa


def includeme(config):
    from iris.service.rest import auth
    config.add_route('confirmation_public_api',
                     'confirmations',
                     static=True,
                     factory=auth.ApiKeyServiceAuthFactory,
                    )
    config.add_route('confirmation_admin_api',
                     'admin/confirmations',
                     static=True,
                     factory=auth.AdminServiceAuthFactory,
                    )
