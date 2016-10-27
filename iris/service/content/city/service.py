from pyramid import security

from lovely.pyrest.rest import RestService, rpcmethod_route, rpcmethod_view

from iris.service import rest
from iris.service.rest import queries
from iris.service.security import acl

from .document import City


@RestService("city_admin_api",
             permission=acl.Permissions.AdminFull)
class CityAdminRESTService(rest.RESTService):

    MAPPER_NAME = 'cities'


@RestService("city_public_api")
class CityPublicRESTService(rest.RESTService):
    """The public city API

    Please note that this class provides the full REST API. Access to the
    endpoints must be limited using swagger (only endpoints defined in swagger
    are available).
    """

    MAPPER_NAME = 'cities'


class CityRESTMapper(rest.DocumentRESTMapperMixin,
                     rest.SearchableDocumentRESTMapperMixin,
                     rest.RESTMapper):
    """A mapper for the petitions admin REST API
    """

    NAME = 'cities'

    DOC_CLASS = City

    QUERY_PARAMS = {
        'ft': queries.fulltextQuery(['tags_ft',
                                     'name_ft',
                                     'zips_ft',
                                    ]),
        'name_ft': queries.fulltextQuery(['name_ft']),
        'tags_ft': queries.fulltextQuery(['tags_ft']),
        'zips_ft': queries.fulltextQuery(['zips_ft']),
    }

    FILTER_PARAMS = {
        'state': queries.termsFilter('state'),
        'provider': queries.termsFilter('provider'),
        'tags': queries.termsFilter('tags'),
        'zips': queries.termsFilter('zips'),
    }

    SORT_PARAMS = {
        'created': queries.fieldSorter('dc.created'),
        'modified': queries.fieldSorter('dc.modified'),
        'id': queries.fieldSorter('id'),
        'state': queries.fieldSorter('state'),
        'provider': queries.fieldSorter('provider'),
        'name': queries.fieldSorter('state'),
        'score': queries.scoreSorter,
        'default': queries.fieldSorter('dc.created', 'DESC'),
    }

    def importer(self, data):
        """Import cities

        Can create, edit or delete cities.

        Expectes data['data'] to be an array of object containing an
        "operation" and "data" (city).
        """
        result = []
        provider = self.request.apikeyProvider
        for entry in data['data']:
            operation = entry.get("operation")
            cityData = entry.get("data")
            if 'id' not in cityData:
                result.append({'status': 'error:missing_id'})
                continue
            city_id = cityData.pop('id')
            city = City.get(City.buildPrimaryKey(city_id, provider))
            if operation == 'delete':
                if city is not None:
                    # TODO: also remove relations
                    city.delete()
                    result.append({'id': city_id,
                                   'irisId': city.id,
                                   'status': 'ok:deleted'})
                else:
                    result.append({'id': city_id,
                                   'status': 'error:not_found'})
            else:
                status = 'ok:updated'
                if city is None:
                    status = 'ok:added'
                    city = City(id=city_id, provider=provider)
                for k, v in cityData.iteritems():
                    if k not in ['id', 'provider']:
                        setattr(city, k, v)
                city.store()
                result.append({'id': city_id,
                               'irisId': city.id,
                               'status': status})
        City.refresh()
        return result


@RestService("city_import_api",
             permission=acl.Permissions.Import)
class CityImportRESTService(rest.BaseRESTService):

    MAPPER_NAME = 'cities'

    @rpcmethod_route(request_method='OPTIONS')
    @rpcmethod_view(http_cache=0,
                    permission=security.NO_PERMISSION_REQUIRED)
    def options(self, **kwargs):
        return {}

    @rpcmethod_route(request_method='POST')
    @rpcmethod_view(http_cache=0)
    def importer(self, **kwargs):
        mapper = self._getMapper(self.MAPPER_NAME)
        data = self.request.swagger_data
        if 'x-iris-api-key' in data:
            del data['x-iris-api-key']
        result = mapper.importer(**data)
        return {"data": result}
