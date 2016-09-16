import copy

from pyramid.response import Response


CORS_HEADERS = {}


def response_factory(request):
    """The response factory for pyramid

    The created response contains the cors headers.
    """
    response = Response()
    global CORS_HEADERS
    headers = copy.copy(CORS_HEADERS)
    origin = request.headers.get('Origin')
    headers['Access-Control-Allow-Origin'] = origin or request.application_url
    response.headers.update(headers)
    return response


def includeme(config):
    global CORS_HEADERS
    settings = config.get_settings()
    for key, value in settings.iteritems():
        if not key.startswith('cors.'):
            continue
        CORS_HEADERS['Access-Control-' + key[5:]] = value
    config.set_response_factory(response_factory)
