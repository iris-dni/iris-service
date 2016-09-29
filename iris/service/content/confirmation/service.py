from pyramid import security

from lovely.pyrest.rest import RestService, rpcmethod_route, rpcmethod_view

from iris.service.errors import Errors
from iris.service import rest
from iris.service.rest.swagger import swagger_reduce_response
from iris.service.rest import queries
from iris.service.security import acl

from .document import Confirmation


@RestService("confirmation_admin_api",
             permission=acl.Permissions.AdminFull)
class ConfirmationAdminRESTService(rest.RESTService):

    MAPPER_NAME = 'confirmations'


@RestService("confirmation_public_api")
class ConfirmationPublicRESTService(rest.RESTService):
    """The service to manage confirmations.

    Please note that this class provides the full REST API. Access to the
    endpoints must be limited using swagger (only endpoints defined in swagger
    are available).
    """

    MAPPER_NAME = 'confirmations'

    @rpcmethod_route(request_method='OPTIONS')
    @rpcmethod_view(http_cache=0,
                    permission=security.NO_PERMISSION_REQUIRED)
    def options_contentId(self, **kwargs):
        return {}

    @rpcmethod_route(request_method='POST')
    @swagger_reduce_response
    def create(self, **kwargs):
        self.prepare_request_data()
        data = self.request.swagger_data['data']['data']
        handler = data.pop('type')
        mapper = self._getMapper(handler)
        try:
            result = mapper.create(**self.request.swagger_data)
        except (KeyError, ValueError) as e:
            raise self.bad_request(replacements={'message': e.message})
        return {"data": result}

    @rpcmethod_route(request_method='OPTIONS',
                     route_suffix='/{token}/confirm')
    @rpcmethod_view(http_cache=0,
                    permission=security.NO_PERMISSION_REQUIRED)
    def options(self, **kwargs):
        return {}

    @rpcmethod_route(request_method='GET',
                     route_suffix='/{token}/confirm')
    @rpcmethod_view(http_cache=0,
                    permission=security.NO_PERMISSION_REQUIRED)
    @swagger_reduce_response
    def confirm(self, **kwargs):
        self.prepare_request_data()
        token = self.request.swagger_data.pop('token')
        confirmation = Confirmation.get(token)
        if confirmation is None:
            raise self.not_found(Errors.document_not_found,
                                 {'contentId': token,
                                  'mapperName': self.MAPPER_NAME
                                 }
                                )
        mapper = self._getMapper(confirmation.handler)
        try:
            result = mapper.confirm(confirmation)
        except (KeyError, ValueError) as e:
            raise self.bad_request(replacements={'message': e.message})
        return {"data": result}

    def _getMapper(self, mapperName):
        mapperName = '.'.join((self.MAPPER_NAME, mapperName))
        return super(
            ConfirmationPublicRESTService, self
        )._getMapper(mapperName)


class ConfirmationRESTMapper(rest.DocumentRESTMapperMixin,
                             rest.SearchableDocumentRESTMapperMixin,
                             rest.RESTMapper):
    """A mapper for the petitions admin REST API
    """

    NAME = 'confirmations'

    DOC_CLASS = Confirmation

    QUERY_PARAMS = {}

    FILTER_PARAMS = {
        'id': queries.termsFilter('id'),
    }

    SORT_PARAMS = {
        'created': queries.fieldSorter('dc.created'),
        'id': queries.fieldSorter('id'),
    }
