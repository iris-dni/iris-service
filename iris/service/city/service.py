from lovely.pyrest.rest import RestService

from iris.service import rest
from iris.service.rest import queries

from .document import City


@RestService("city_admin_api")
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
