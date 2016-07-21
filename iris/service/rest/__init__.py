from .service import RESTService, RESTMapper, BaseRESTService  # noqa
from .document import (  # noqa
    DocumentRESTMapperMixin,
    SearchableDocumentRESTMapperMixin,
)


def includeme(config):
    pass
