from . import service  # noqa


def includeme(config):
    config.add_route('statemachine_api',
                     'admin/statemachine',
                     static=True,
                    )
