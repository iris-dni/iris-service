from . import service  # noqa
from .document import Petition  # noqa


def includeme(config):
    from iris.service.rest import auth
    config.add_route('petition_public_api',
                     'petitions',
                     static=True,
                     factory=auth.AdminServiceAuthFactory,
                    )
    config.add_route('petition_by_token_api',
                     'token',
                     static=True)
    config.add_route('petition_admin_api',
                     'admin/petitions',
                     static=True,
                     factory=auth.AdminServiceAuthFactory,
                    )
    config.add_route('supporter_admin_api',
                     'admin/supporters',
                     static=True,
                     factory=auth.AdminServiceAuthFactory,
                    )
