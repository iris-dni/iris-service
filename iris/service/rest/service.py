import logging
import copy
from functools import partial

from pyramid import security
from pyramid.request import Request

from lovely.pyrest.rest import rpcmethod_route, rpcmethod_view

from ..errors import Errors
from ..endpoint import EndpointErrorMixin

from .swagger import swagger_reduce_response
from .extender import APIExtender
from .transform import APITransformer


log = logging.getLogger(__name__)


class BaseRESTService(EndpointErrorMixin):
    """The base implementation for mapped REST services

    A mapped REST service is implemented using a registered mapper. The data
    access part is implemented in the mapper.
    """

    def __init__(self, request):
        self.request = request

    def _getMapper(self, mapperName, method=None):
        """Get a mapper by name

        Also check if the `method` exists on the mapper.

        raise a 404 error if the mapper or the method could not be found.
        """
        try:
            mapper = RESTMapper.getMapperImplementation(mapperName,
                                                        self.request)
            if method is not None and not hasattr(mapper, method):
                raise KeyError()
            return mapper
        except KeyError:
            raise self.not_found(Errors.mapper_not_found,
                                 {'mapperName': mapperName}
                                )

    def _mapperName(self, offset):
        return self.request.path.split('/')[offset]

    def get_content(self, mapperName, contentId, resolve=[], extend=[]):
        mapper = self._getMapper(mapperName)
        try:
            data = mapper.get(contentId, resolve, extend)
        except NotImplementedError as e:
            raise self.method_not_allowed(replacements={'message': e.message})
        if data is None:
            raise self.not_found(Errors.document_not_found,
                                 {'contentId': contentId,
                                  'mapperName': mapperName
                                 }
                                )
        multirequest = isinstance(contentId, list) and len(contentId) > 1
        if multirequest:
            return {"items": data}
        else:
            return {"data": data}

    def create_content(self, mapperName, data, resolve=[], extend=[]):
        mapper = self._getMapper(mapperName)
        try:
            data = mapper.create(data, resolve, extend)
        except NotImplementedError as e:
            raise self.method_not_allowed(replacements={'message': e.message})
        return {"data": data}

    def update_content(self, mapperName, contentId, data,
                       resolve=[], extend=[]):
        mapper = self._getMapper(mapperName)
        try:
            data = mapper.update(contentId, data, resolve, extend)
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
        try:
            data = mapper.search(**kwargs)
        except (KeyError, ValueError) as e:
            raise self.bad_request(replacements={'message': e.message})
        except NotImplementedError as e:
            raise self.method_not_allowed(replacements={'message': e.message})
        return data

    def prepare_request_data(self):
        data = self.request.swagger_data
        if 'x-iris-api-key' in data:
            del data['x-iris-api-key']


class RESTService(BaseRESTService):
    """A generic REST implementation

    This view forwards the requests to a `mapper`.
    """

    @rpcmethod_route(request_method='OPTIONS')
    @rpcmethod_view(http_cache=0,
                    permission=security.NO_PERMISSION_REQUIRED)
    def options(self, **kwargs):
        return {}

    @rpcmethod_route(request_method='GET')
    @rpcmethod_view(http_cache=0)
    @swagger_reduce_response
    def search(self, **kwargs):
        self.prepare_request_data()
        return self.search_content(self.MAPPER_NAME,
                                   **self.request.swagger_data)

    @rpcmethod_route(request_method='OPTIONS',
                     route_suffix='/{contentId}')
    @rpcmethod_view(http_cache=0,
                    permission=security.NO_PERMISSION_REQUIRED)
    def options_contentId(self, **kwargs):
        return {}

    @rpcmethod_route(request_method='GET',
                     route_suffix='/{contentId}')
    @rpcmethod_view(http_cache=0)
    @swagger_reduce_response
    def get(self, **kwargs):
        self.prepare_request_data()
        return self.get_content(self.MAPPER_NAME,
                                **self.request.swagger_data)

    @rpcmethod_route(request_method='POST')
    @swagger_reduce_response
    def create(self, **kwargs):
        self.prepare_request_data()
        return self.create_content(self.MAPPER_NAME,
                                   **self.request.swagger_data)

    @rpcmethod_route(request_method='POST',
                     route_suffix='/{contentId}')
    @swagger_reduce_response
    def update(self, **kwargs):
        self.prepare_request_data()
        return self.update_content(self.MAPPER_NAME,
                                   **self.request.swagger_data)

    @rpcmethod_route(request_method='DELETE',
                     route_suffix='/{contentId}')
    @swagger_reduce_response
    def delete(self, **kwargs):
        self.prepare_request_data()
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

    def get(self, contentId, resolve, extend):
        raise NotImplementedError('%s.get' % self.__class__.__name__)

    def create(self, data, resolve, extend):
        raise NotImplementedError('%s.create' % self.__class__.__name__)

    def update(self, contentId, data, resolve, extend):
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


def to_api(request, doc, resolve=None, extend=None):
    """Provide the document as a dict to be able to JSON serialize it

    This method is added to all requests.
    """
    if doc is None:
        return None
    if resolve is None:
        resolve = request.swagger_data.get('resolve', [])
    if extend is None:
        extend = request.swagger_data.get('extend', [])
    extender = APIExtender(request, doc, extend)
    result = APITransformer(doc, resolve=resolve).to_api()
    extender.extend(result)
    return result


def blank_request():
    """Try to create a working request instance
    """
    request = Request.blank('/')
    request.to_api = partial(to_api, request)
    request.context = None
    return request


TESTING_STATE = []


def testing_push_state():
    global TESTING_STATE
    TESTING_STATE.append(copy.copy(RESTMapper._MAPPER_REGISTRY))


def testing_pop_state():
    global TESTING_STATE
    RESTMapper._MAPPER_REGISTRY = TESTING_STATE.pop()


def includeme(config):
    config.add_request_method(to_api, "to_api")
