from .document import File  # noqa


def includeme(config):
    config.add_route('blob_api',
                     '/blobs',
                     static=True)
