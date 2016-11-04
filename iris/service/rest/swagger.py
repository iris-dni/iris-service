from pyramid_swagger import tween
from pyramid_swagger import api
from pyramid.interfaces import IRoutesMapper

TWEEN_SETTINGS = None

SPEC_MAPPING_CACHE = {}


def swagger_reduce_response(f):
    """Reduce response JSON data from swagger response definition

    This is a decorator for pyramid views.
    """

    def do(self, *args, **kwargs):
        return reduce_result(self.request,
                             f(self, *args, **kwargs),
                            )
    return do


def reduce_result(request, result):
    global TWEEN_SETTINGS, SPEC_MAPPING_CACHE
    route_mapper = request.registry.queryUtility(IRoutesMapper)
    if route_mapper is None:
        # for testing
        return result
    route_info = route_mapper(request)
    route = route_info['route']
    cacheKey = route.path + route.predicates[0].text()
    if cacheKey not in SPEC_MAPPING_CACHE:
        if TWEEN_SETTINGS is None:
            TWEEN_SETTINGS = tween.load_settings(request.registry)
        swagger_handler, spec = tween.get_swagger_objects(
            TWEEN_SETTINGS,
            route_info,
            request.registry
        )
        op = swagger_handler.op_for_request(
            request,
            route_info=route_info,
            spec=spec
        )
        response_spec = tween.get_response_spec(
            request.response.status_int, op
        )
        resolved = api.resolve_refs(spec, response_spec).get('schema', {})
        spec_mapping = build_spec_mapping(resolved)
        SPEC_MAPPING_CACHE[cacheKey] = spec_mapping
    else:
        spec_mapping = SPEC_MAPPING_CACHE[cacheKey]
    return reduce_mapping(spec_mapping, result)


def reduce_mapping(mapping, data):
    """Reduce data to contain only properties from mapping
    """
    if mapping is True:
        return data
    if data is None:
        return data
    result = {}
    for k, v in mapping.iteritems():
        if data is None or k not in data:
            continue
        prop = data[k]
        if v is True:
            result[k] = prop
        elif isinstance(v, dict):
            result[k] = reduce_mapping(v, prop)
        elif isinstance(v, list):
            result[k] = [reduce_mapping(v[0], c) for c in prop]
    return result


def build_spec_mapping(spec):
    """From a swagger spec dict create a simple dict with all properties

    Reduces a full swagger spec to a simple dict which only contains the
    properties. The result can then be used to reduce any dict to contain only
    properties from the spec using method `reduce_mapping`.
    """
    result = {}
    spec_type = spec.get('type')
    if spec_type == 'object':
        if 'properties' in spec:
            # extract all properties into the result
            for k, v in spec['properties'].iteritems():
                result[k] = build_spec_mapping(v)
        elif 'allOf' in spec:
            # combine all entries into the result
            for c in spec['allOf']:
                result.update(build_spec_mapping(c))
    elif spec_type == 'array':
        if 'items' in spec:
            return [build_spec_mapping(spec['items'])]
    return result or True
