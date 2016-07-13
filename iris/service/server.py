from pyramid.config import Configurator

from gevent.pywsgi import WSGIServer, WSGIHandler

API_V1_BASE_URL = '/v1'
API_Vx_BASE_URL = '/v{version}'


class LoggingWSGIHandler(WSGIHandler):

    def log_request(self):
        # do not log each request
        pass


def server_factory(global_conf, host, port):
    """Provide the WSGI server for paste

    This must be setup as the paste.server_factory in the egg entry-points.
    """
    port = int(port)

    def serve(app):
        def theapp(environ, start_response):
            environ["wsgi.url_scheme"] = environ.get("HTTP_X_FORWARDED_PROTO",
                                                     "http")
            return app(environ, start_response)

        WSGIServer(
            (host, port),
            theapp,
            handler_class=LoggingWSGIHandler,
        ).serve_forever()
    return serve


def app_factory(global_config, **settings):
    config = Configurator(
        settings=settings,
        autocommit=True,
    )

    config.include('iris.service.db')
    config.include('iris.service.rest')
    config.include('iris.service.static')
    config.include('iris.service.sample.service',
                   route_prefix=API_Vx_BASE_URL)
    config.include('iris.service.routes_api',
                   route_prefix=API_Vx_BASE_URL)

    config.scan('iris.service.rest')
    config.scan('iris.service.petition')
    config.scan('iris.service.static')
    config.scan('iris.service.sample.service')

    return config.make_wsgi_app()
