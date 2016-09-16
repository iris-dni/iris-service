from . import schedule


def includeme(config):
    settings = config.get_settings()
    config.add_route('ogcheck',
                     '/og/check',
                     static=True)
    if 'og.noworker' not in settings:
        schedule.Worker().start()
