from lovely.pyrest.rest import RestService, rpcmethod_route, rpcmethod_view

from iris.service import rest
from iris.service.rest import queries
from iris.service.security import acl

from .document import City


@RestService("city_admin_api",
             permission=acl.Permissions.AdminFull)
class CityAdminRESTService(rest.RESTService):

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
        'tags_ft': queries.fulltextQuery(['tags_ft']),
        'name_ft': queries.fulltextQuery(['name_ft']),
        'zips_ft': queries.fulltextQuery(['zips_ft']),
    }

    FILTER_PARAMS = {
        'state': queries.termsFilter('state'),
        'tags': queries.termsFilter('tags'),
    }

    SORT_PARAMS = {
        'created': queries.fieldSorter('dc.created'),
        'modified': queries.fieldSorter('dc.modified'),
        'id': queries.fieldSorter('id'),
        'state': queries.fieldSorter('state'),
        'name': queries.fieldSorter('state'),
        'score': queries.scoreSorter,
        'default': queries.fieldSorter('dc.created', 'DESC'),
    }

    def importer(self, data):
        """Import cities
        """
        result = []
        for city_data in data['data']:
            if 'id' in city_data:
                city_id = city_data.pop('id')
                city = City.get(city_id)
                if city is None:
                    city = City(id=city_id)
                for k, v in city_data.iteritems():
                    setattr(city, k, v)
                city.store()
                result.append({'id': city.id, 'status': 'ok'})
            else:
                result.append({'status': 'missing id'})
        City.refresh()
        return result


@RestService("city_import_api",
             permission=acl.Permissions.Edit)
class CityImportRESTService(rest.BaseRESTService):

    MAPPER_NAME = 'cities'

    @rpcmethod_route(request_method='OPTIONS')
    @rpcmethod_view(http_cache=0)
    def options(self, **kwargs):
        return {}

    @rpcmethod_route(request_method='POST')
    @rpcmethod_view(http_cache=0)
    def importer(self, **kwargs):
        mapper = self._getMapper(self.MAPPER_NAME)
        result = mapper.importer(**self.request.swagger_data)
        return {"data": result}
