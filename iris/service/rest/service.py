import logging
import copy

from lovely.pyrest.rest import RestService, rpcmethod_route, rpcmethod_view

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
            return RESTMapper.getMapperImplementation(mapperName)
        except KeyError:
            raise self.not_found(Errors.mapper_not_found,
                                 {'mapperName': mapperName}
                                )

    def _queryParams(self):
        queryParams = {k: v for k, v in self.request.GET.items()}
        if 'resolve' in queryParams:
            queryParams['resolve'] = [
                n.strip()
                for n in queryParams['resolve'].split(',')
                if n.strip()]
        return queryParams

    def get_content(self, mapperName, contentId):
        mapper = self._getMapper(mapperName)
        try:
            data = mapper.get(contentId)
        except NotImplementedError as e:
            raise self.method_not_allowed(e.message)
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
            raise self.method_not_allowed(e.message)
        return {"data": data}

    def update_content(self, mapperName, contentId, data):
        mapper = self._getMapper(mapperName)
        try:
            data = mapper.update(contentId, data)
        except NotImplementedError as e:
            raise self.method_not_allowed(e.message)
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
            raise self.method_not_allowed(e.message)
        if data is None:
            raise self.not_found(Errors.document_not_found,
                                 {'contentId': contentId,
                                  'mapperName': mapperName
                                 }
                                )
        return {"data": data}

    def search_content(self, mapperName):
        mapper = self._getMapper(mapperName)
        queryParams = self._queryParams()
        try:
            data = mapper.search(**queryParams)
        except (KeyError, ValueError) as e:
            raise self.bad_request(e.message)
        except NotImplementedError as e:
            raise self.method_not_allowed(e.message)
        return data


@RestService("generic_rest_service")
class RESTService(BaseRESTService):

    @rpcmethod_route(route_suffix='/{mapperName}/{contentId}')
    @rpcmethod_view(http_cache=0)
    def get(self, mapperName, contentId, **kwargs):
        return self.get_content(mapperName, contentId)

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{mapperName}')
    def create(self, mapperName, data, **kwargs):
        return self.create_content(mapperName, data)

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{mapperName}/{contentId}')
    def update(self, mapperName, contentId, data, **kwargs):
        return self.update_content(mapperName, contentId, data)

    @rpcmethod_route(request_method='DELETE',
                     route_suffix='/{mapperName}/{contentId}')
    def delete(self, mapperName, contentId, **kwargs):
        return self.delete_content(mapperName, contentId)

    @rpcmethod_route(route_suffix='/{mapperName}')
    @rpcmethod_view(http_cache=0)
    def search(self, mapperName, **kwargs):
        return self.search_content(mapperName)


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
