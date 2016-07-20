from pyramid.events import NewRequest


CORS_HEADERS = {}


def add_cors_headers_response_callback(event):
    def cors_headers(request, response):
        global CORS_HEADERS
        response.headers.update(CORS_HEADERS)
    event.request.add_response_callback(cors_headers)


def includeme(config):
    global CORS_HEADERS
    settings = config.get_settings()
    for key, value in settings.iteritems():
        if not key.startswith('cors.'):
            continue
        CORS_HEADERS['Access-Control-' + key[5:]] = value
    config.add_subscriber(add_cors_headers_response_callback, NewRequest)
