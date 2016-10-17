from .document import File  # noqa


def includeme(config):
    config.add_route('file_api',
                     '/files',
                     static=True)
