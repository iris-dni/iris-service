import logging
import copy

from lovely.pyrest.rest import rpcmethod_route, rpcmethod_view

from .swagger import swagger_reduce_response
from ..errors import Errors
from ..endpoint import EndpointErrorMixin


log = logging.getLogger(__name__)


class BaseRESTService(EndpointErrorMixin):
    """The base implementation for mapped REST services

    A mapped REST service is implemented using a registered mapper. The data
    access part is implemented in the mapper.
    """

    def __init__(self, request):
        self.request = request

    def _getMapper(self, mapperName):
        try:
            return RESTMapper.getMapperImplementation(mapperName, self.request)
        except KeyError:
            raise self.not_found(Errors.mapper_not_found,
                                 {'mapperName': mapperName}
                                )

    def _queryParams(self, params):
        queryParams = {k: v for k, v in params.items()}
        if 'resolve' in queryParams:
            queryParams['resolve'] = [
                n.strip()
                for n in queryParams['resolve'].split(',')
                if n.strip()]
        return queryParams

    def _mapperName(self, offset):
        return self.request.path.split('/')[offset]

    def get_content(self, mapperName, contentId):
        mapper = self._getMapper(mapperName)
        try:
            data = mapper.get(contentId)
        except NotImplementedError as e:
            raise self.method_not_allowed(replacements={'message': e.message})
        if data is None:
            raise self.not_found(Errors.document_not_found,
                                 {'contentId': contentId,
                                  'mapperName': mapperName
                                 }
                                )
        return {"data": data}

    def create_content(self, mapperName, data):
        mapper = self._getMapper(mapperName)
        try:
            data = mapper.create(data)
        except NotImplementedError as e:
            raise self.method_not_allowed(replacements={'message': e.message})
        return {"data": data}

    def update_content(self, mapperName, contentId, data):
        mapper = self._getMapper(mapperName)
        try:
            data = mapper.update(contentId, data)
        except NotImplementedError as e:
            raise self.method_not_allowed(replacements={'message': e.message})
        if data is None:
            raise self.not_found(Errors.document_not_found,
                                 {'contentId': contentId,
                                  'mapperName': mapperName
                                 }
                                )
        return {"data": data}

    def delete_content(self, mapperName, contentId):
        mapper = self._getMapper(mapperName)
        try:
            data = mapper.delete(contentId)
        except NotImplementedError as e:
            raise self.method_not_allowed(replacements={'message': e.message})
        if data is None:
            raise self.not_found(Errors.document_not_found,
                                 {'contentId': contentId,
                                  'mapperName': mapperName
                                 }
                                )
        return {"data": data}

    def search_content(self, mapperName, **kwargs):
        mapper = self._getMapper(mapperName)
        queryParams = self._queryParams(kwargs)
        try:
            data = mapper.search(**queryParams)
        except (KeyError, ValueError) as e:
            raise self.bad_request(replacements={'message': e.message})
        except NotImplementedError as e:
            raise self.method_not_allowed(replacements={'message': e.message})
        return data


class RESTService(BaseRESTService):
    """A generic REST implementation

    This view forwards the requests to a `mapper`.
    """

    @rpcmethod_route(request_method='OPTIONS')
    @rpcmethod_view(http_cache=0)
    def options(self, **kwargs):
        return {}

    @rpcmethod_route(request_method='GET')
    @rpcmethod_view(http_cache=0)
    @swagger_reduce_response
    def search(self, **kwargs):
        return self.search_content(self.MAPPER_NAME,
                                   **self.request.swagger_data)

    @rpcmethod_route(request_method='OPTIONS',
                     route_suffix='/{contentId}')
    @rpcmethod_view(http_cache=0)
    def options_contentId(self, **kwargs):
        return {}

    @rpcmethod_route(request_method='GET',
                     route_suffix='/{contentId}')
    @swagger_reduce_response
    @rpcmethod_view(http_cache=0)
    def get(self, **kwargs):
        return self.get_content(self.MAPPER_NAME,
                                **self.request.swagger_data)

    @rpcmethod_route(request_method='POST')
    @swagger_reduce_response
    def create(self, **kwargs):
        return self.create_content(self.MAPPER_NAME,
                                   **self.request.swagger_data)

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}')
    @swagger_reduce_response
    def update(self, **kwargs):
        return self.update_content(self.MAPPER_NAME,
                                   **self.request.swagger_data)

    @rpcmethod_route(request_method='DELETE',
                     route_suffix='/{contentId}')
    @swagger_reduce_response
    def delete(self, **kwargs):
        return self.delete_content(self.MAPPER_NAME,
                                   **self.request.swagger_data)


class RESTMapperMeta(type):
    """Metaclass for the RESTMapper

    Registers the mapper.
    """

    def __init__(cls, name, bases, dct):
        if cls.__name__ != 'RESTMapper':
            if not cls.NAME:
                raise ValueError('%s.NAME not set' % name)
            if cls.NAME in cls._MAPPER_REGISTRY:
                raise NameError(
                    'Duplicate name "%s", conflicting classes: "%s"-"%s"' % (
                        cls.NAME,
                        cls._MAPPER_REGISTRY[cls.NAME].__name__,
                        name
                    )
                )
            cls._MAPPER_REGISTRY[cls.NAME] = cls
            log.info('registered RESTMapper "%s" for class "%s"',
                     cls.NAME,
                     name)
        super(RESTMapperMeta, cls).__init__(name, bases, dct)


class RESTMapper(object):

    __metaclass__ = RESTMapperMeta

    _MAPPER_REGISTRY = {}

    NAME = None

    def __init__(self, request):
        self.request = request

    def get(self, contentId):
        raise NotImplementedError('%s.get' % self.__class__.__name__)

    def create(self, data):
        raise NotImplementedError('%s.create' % self.__class__.__name__)

    def update(self, contentId, data):
        raise NotImplementedError('%s.update' % self.__class__.__name__)

    def delete(self, contentId):
        raise NotImplementedError('%s.delete' % self.__class__.__name__)

    def search(self, **kwargs):
        raise NotImplementedError('%s.search' % self.__class__.__name__)

    @classmethod
    def getMapperImplementation(cls, name, request):
        cls = cls._MAPPER_REGISTRY[name]
        impl = cls(request)
        impl.name = name
        return impl


TESTING_STATE = []


def testing_push_state():
    global TESTING_STATE
    TESTING_STATE.append(copy.copy(RESTMapper._MAPPER_REGISTRY))


def testing_pop_state():
    global TESTING_STATE
    RESTMapper._MAPPER_REGISTRY = TESTING_STATE.pop()
