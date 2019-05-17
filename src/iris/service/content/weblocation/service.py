from lovely.pyrest.rest import RestService, rpcmethod_route, rpcmethod_view

from iris.service.rest.swagger import swagger_reduce_response
from iris.service.errors import Errors

from iris.service import rest
from iris.service.rest import queries
from iris.service.security import acl

from .document import WebLocation


@RestService("weblocation_admin_api",
             permission=acl.Permissions.AdminFull)
class WebLocationAdminRESTService(rest.RESTService):

    MAPPER_NAME = 'weblocations'

    @rpcmethod_route(request_method='GET',
                     route_suffix='/{contentId}/resetog')
    @rpcmethod_view(http_cache=0)
    @swagger_reduce_response
    def resetog(self, **kwargs):
        return self.do_resetog(self.MAPPER_NAME,
                               **self.request.swagger_data)

    def do_resetog(self, mapperName, contentId, resolve=[]):
        mapper = self._getMapper(mapperName)
        try:
            data = mapper.resetog(contentId, resolve)
        except NotImplementedError as e:
            raise self.method_not_allowed(replacements={'message': e.message})
        if data is None:
            raise self.not_found(Errors.document_not_found,
                                 {'contentId': contentId,
                                  'mapperName': mapperName
                                 }
                                )
        return {"data": data}


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

    def resetog(self, contentId, resolve=[]):
        loc = self.DOC_CLASS.get(contentId)
        if loc is None:
            return None
        loc.og = None
        loc.store(refresh=True)
        return self.to_api(loc, resolve)
