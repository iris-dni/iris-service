from lovely.pyrest.rest import RestService

from iris.service import rest
from iris.service.rest import queries

from .document import User


@RestService("user_admin_api")
class PetitionAdminRESTService(rest.RESTService):

    MAPPER_NAME = 'users'


class UsersRESTMapper(rest.DocumentRESTMapperMixin,
                      rest.SearchableDocumentRESTMapperMixin,
                      rest.RESTMapper):
    """A mapper for the petitions admin REST API
    """

    NAME = 'users'

    DOC_CLASS = User

    QUERY_PARAMS = {
        'state': queries.termsFilter('state'),
        'roles': queries.termsFilter('roles'),
        'sso.provider': queries.termsFilter('sso.provider'),
        'sso.trusted': queries.booleanFilter('sso.trusted'),
        'ft': queries.fulltextQuery(['firstname_ft',
                                     'lastname_ft',
                                     'email_ft',
                                    ]),
        'email_ft': queries.fulltextQuery(['email_ft']),
        'firstname_ft': queries.fulltextQuery(['firstname_ft']),
        'lastname_ft': queries.fulltextQuery(['lastname_ft']),
    }

    SORT_PARAMS = {
        'created': queries.fieldSorter('dc.created'),
        'modified': queries.fieldSorter('dc.modified'),
        'firstname': queries.fieldSorter('firstname'),
        'lastname': queries.fieldSorter('lastname'),
        'score': queries.scoreSorter,
        'default': queries.fieldSorter('dc.created', 'DESC'),
    }
