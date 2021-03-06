from . import service  # noqa
from . import confirmation  # noqa
from .document import Petition  # noqa
from pyramid.settings import aslist


SETTINGS = {}


def includeme(config):
    from iris.service.rest import auth
    from .acl import (
        PublicPetitionServiceAuthFactory,
        SupportersTokenServiceAuthFactory,
    )
    config.add_route('petition_public_api',
                     'petitions',
                     static=True,
                     factory=PublicPetitionServiceAuthFactory,
                    )
    config.add_route('petition_by_token_api',
                     'token',
                     static=True)
    config.add_route('petition_admin_api',
                     'admin/petitions',
                     static=True,
                     factory=auth.AdminServiceAuthFactory,
                    )
    config.add_route('supporter_public_api',
                     'supporters',
                     static=True,
                     factory=SupportersTokenServiceAuthFactory,
                    )
    config.add_route('supporter_admin_api',
                     'admin/supporters',
                     static=True,
                     factory=auth.AdminServiceAuthFactory,
                    )
    settings = config.get_settings()
    petitions_cron = settings.get('statemachine.petitions.cron')
    if petitions_cron:
        from iris.service.elector import Elector
        from iris.service import cron
        from . import schedule
        cron.distributed_spawn(schedule.TickWorker(),
                               petitions_cron,
                               Elector('statemachine.petitions.cron')
                              )
    global SETTINGS
    mail = SETTINGS['frontend'] = {}
    mail['domain'] = settings.get('frontend.domain')
    mail['petition-email-confirmpath'] = settings.get(
                                            'frontend.petition.confirmpath')
    mail['supporter-email-confirmpath'] = settings.get(
                                            'frontend.supporter.confirmpath')
    petition = SETTINGS['petition'] = {}
    petition['urls'] = {}
    for name, value in settings.iteritems():
        if name.startswith('frontend.petition.urls.'):
            petition['urls'][name[23:]] = value
    SETTINGS['domains.automatic_mentions'] = aslist(
                                settings.get('domains.automatic_mentions', ''))
