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
        global TWEEN_SETTINGS, SPEC_MAPPING_CACHE
        # call the view method
        result = f(self, *args, **kwargs)
        route_mapper = self.request.registry.queryUtility(IRoutesMapper)
        route_info = route_mapper(self.request)
        path = route_info['route'].path
        if path not in SPEC_MAPPING_CACHE:
            if TWEEN_SETTINGS is None:
                TWEEN_SETTINGS = tween.load_settings(self.request.registry)
            swagger_handler, spec = tween.get_swagger_objects(
                TWEEN_SETTINGS,
                route_info,
                self.request.registry
            )
            op = swagger_handler.op_for_request(
                self.request,
                route_info=route_info,
                spec=spec
            )
            response_spec = tween.get_response_spec(
                self.request.response.status_int, op
            )
            resolved = api.resolve_refs(spec, response_spec).get('schema', {})
            spec_mapping = build_spec_mapping(resolved)
            SPEC_MAPPING_CACHE[path] = spec_mapping
        else:
            spec_mapping = SPEC_MAPPING_CACHE[path]
        return reduce_mapping(spec_mapping, result)
    return do


def reduce_mapping(mapping, data):
    """Reduce data to conain only properties from mapping
    """
    result = {}
    for k, v in mapping.iteritems():
        if k not in data:
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
