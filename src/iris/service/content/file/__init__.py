from .document import File  # noqa


def includeme(config):
    from iris.service.rest import auth
    config.add_route('file_public_api',
                     'files',
                     static=True)
    config.add_route('file_admin_api',
                     'admin/files',
                     static=True,
                     factory=auth.AdminServiceAuthFactory)
