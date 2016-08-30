from lovely.pyrest.rest import RestService

from iris.service import rest
from iris.service.rest import queries
from iris.service.security import acl

from .document import WebLocation


@RestService("weblocation_admin_api",
             permission=acl.Permissions.AdminFull)
class WebLocationAdminRESTService(rest.RESTService):

    MAPPER_NAME = 'weblocations'


@RestService("weblocation_public_api")
class WebLocationPublicRESTService(rest.RESTService):
    """The public web location API

    Please note that this class provides the full REST API. Access to the
    endpoints must be limited using swagger (only endpoints defined in swagger
    are available).
    """

    MAPPER_NAME = 'weblocations'


class WebLocationRESTMapper(rest.DocumentRESTMapperMixin,
                            rest.SearchableDocumentRESTMapperMixin,
                            rest.RESTMapper):
    """A mapper for the weblocation REST API
    """

    NAME = 'weblocations'

    DOC_CLASS = WebLocation

    QUERY_PARAMS = {
    }

    FILTER_PARAMS = {
        'state': queries.termsFilter('state'),
    }

    SORT_PARAMS = {
        'created': queries.fieldSorter('dc.created'),
        'modified': queries.fieldSorter('dc.modified'),
        'id': queries.fieldSorter('id'),
        'state': queries.fieldSorter('state'),
        'default': queries.fieldSorter('dc.created', 'DESC'),
    }
