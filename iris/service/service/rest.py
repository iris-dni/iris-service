import logging
import copy

from pyramid.httpexceptions import (
    HTTPNotFound,
    HTTPBadRequest,
    HTTPMethodNotAllowed,
)

from lovely.pyrest.rest import RestService, rpcmethod_route, rpcmethod_view


log = logging.getLogger(__name__)


class BaseRESTService(object):
    """The base implementation for mapped REST services

    A mapped REST service is implemented using a registered mapper. The data
    access part is implemented in the mapper.
    """

    def __init__(self, request):
        self.request = request

    def _getMapper(self, mapperName):
        try:
            return RESTMapper.getMapperImplementation(mapperName)
        except KeyError:
            raise HTTPNotFound("Mapper '%s' not found" % mapperName)

    def _queryParams(self):
        queryParams = {k: v for k, v in self.request.GET.items()}
        if 'resolve' in queryParams:
            queryParams['resolve'] = [
                n.strip()
                for n in queryParams['resolve'].split(',')
                if n.strip()]
        return queryParams


@RestService("generic_rest_service")
class RESTService(BaseRESTService):

    @rpcmethod_route(route_suffix='/{mapperName}/{contentId}')
    @rpcmethod_view(http_cache=0)
    def get(self, mapperName, contentId, **kwargs):
        mapper = self._getMapper(mapperName)
        queryParams = self._queryParams()
        resolve = ['all']
        properties = None
        if 'resolve' in queryParams:
            resolve = queryParams.pop('resolve')
        if 'properties' in queryParams:
            properties = queryParams.pop('properties')
        if queryParams:
            raise HTTPBadRequest('unknown query parameters, '
                                 'only resolve is allowed')
        try:
            data = mapper.get(contentId)
        except NotImplementedError as e:
            raise HTTPMethodNotAllowed(e.message)
        if data is None:
            raise HTTPNotFound(
                "Id %s of content type '%s' not found" % (contentId,
                                                          mapperName)
            )
        return {"data": data}

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{mapperName}')
    def create(self, mapperName, data, **kwargs):
        mapper = self._getMapper(mapperName)
        try:
            data = mapper.create(data)
        except NotImplementedError as e:
            raise HTTPMethodNotAllowed(e.message)
        return {"data": data}

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{mapperName}/{contentId}')
    def update(self, mapperName, contentId, data, **kwargs):
        mapper = self._getMapper(mapperName)
        try:
            data = mapper.update(contentId, data)
        except NotImplementedError as e:
            raise HTTPMethodNotAllowed(e.message)
        return {"data": data}

    @rpcmethod_route(route_suffix='/{mapperName}')
    @rpcmethod_view(http_cache=0)
    def query(self, mapperName, **kwargs):
        mapper = self._getMapper(mapperName)
        queryParams = self._queryParams()
        try:
            data = mapper.query(**queryParams)
        except (KeyError, ValueError) as e:
            raise HTTPBadRequest(e.message)
        except NotImplementedError as e:
            raise HTTPMethodNotAllowed(e.message)
        return data


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
            log.info('registered RESTMapper "%s" for class "%s"', cls.NAME, name)
        super(RESTMapperMeta, cls).__init__(name, bases, dct)


class RESTMapper(object):

    __metaclass__ = RESTMapperMeta

    _MAPPER_REGISTRY = {}

    NAME = None

    def get(self, contentId):
        raise NotImplementedError('%s.get' % self.__class__.__name__)

    def create(self, data):
        raise NotImplementedError('%s.create' % self.__class__.__name__)

    def update(self, contentId, data):
        raise NotImplementedError('%s.update' % self.__class__.__name__)

    def query(self, **kwargs):
        raise NotImplementedError('%s.query' % self.__class__.__name__)

    @classmethod
    def getMapperImplementation(cls, name):
        cls = cls._MAPPER_REGISTRY[name]
        impl = cls()
        impl.name = name
        return impl


TESTING_STATE = []


def testing_push_state():
    global TESTING_STATE
    TESTING_STATE.append(copy.copy(RESTMapper._MAPPER_REGISTRY))


def testing_pop_state():
    global TESTING_STATE
    RESTMapper._MAPPER_REGISTRY = TESTING_STATE.pop()


def includeme(config):
    pass