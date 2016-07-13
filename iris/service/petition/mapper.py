from iris.service import rest

from .document import Petition


class PetitionsRESTMapper(rest.DocumentRESTMapperMixin, rest.RESTMapper):
    """A mapper for the petitions admin REST API
    """

    NAME = 'petitions'

    DOC_CLASS = Petition
