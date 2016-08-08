import copy

from pyramid.events import NewRequest


CORS_HEADERS = {}


def add_cors_headers_response_callback(event):
    def cors_headers(request, response):
        global CORS_HEADERS
        headers = copy.copy(CORS_HEADERS)
        origin = request.headers.get('Origin')
        headers['Access-Control-Allow-Origin'] = origin or request.application_url
        response.headers.update(headers)
    event.request.add_response_callback(cors_headers)


def includeme(config):
    global CORS_HEADERS
    settings = config.get_settings()
    for key, value in settings.iteritems():
        if not key.startswith('cors.'):
            continue
        CORS_HEADERS['Access-Control-' + key[5:]] = value
    config.add_subscriber(add_cors_headers_response_callback, NewRequest)
