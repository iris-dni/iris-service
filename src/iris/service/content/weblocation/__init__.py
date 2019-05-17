from .document import WebLocation  # noqa


def includeme(config):
    from iris.service.rest import auth
    config.add_route('weblocation_public_api',
                     'weblocations',
                     static=True,
                    )
    config.add_route('weblocation_admin_api',
                     'admin/weblocations',
                     static=True,
                     factory=auth.AdminServiceAuthFactory,
                    )
