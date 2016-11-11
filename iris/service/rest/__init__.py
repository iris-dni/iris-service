from .service import (  # noqa
    RESTService,
    RESTMapper,
    BaseRESTService,
    blank_request,
)
from .document import (  # noqa
    DocumentRESTMapperMixin,
    SearchableDocumentRESTMapperMixin,
)

APP_URL = None


def includeme(config):
    global APP_URL
    settings = config.get_settings()
    APP_URL = settings.get('api.app_url', None)
