from gevent import monkey
monkey.patch_all()

import os

from pyramid.settings import asbool
from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid import security

from gevent.pywsgi import WSGIServer, WSGIHandler

from .security.security import groupfinder
from .security.policy import IRISAuthPolicy


API_V1_BASE_URL = '/v1'


class Root(object):
    __acl__ = [
        (security.Allow, security.Authenticated, 'view'),
        (security.Allow, 'group:public', 'view'),
    ]

    def __init__(self, request):
        self.request = request


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

    authz_policy = ACLAuthorizationPolicy()
    authn_policy = IRISAuthPolicy(
        secret=settings['auth.secret'],
        cookie_name=settings['auth.cookie_name'],
        timeout=settings.get('auth.timeout', None),
        reissue_time=settings.get('auth.reissue_time', None),
        max_age=settings.get('auth.max_age', None),
        parent_domain=asbool(settings.get('auth.parent_domain', 'true')),

        callback=groupfinder,
    )

    config = Configurator(
        settings=settings,

        authentication_policy=authn_policy,
        authorization_policy=authz_policy,

        root_factory=Root,

        autocommit=True,
    )

    settings = config.get_settings()
    settings['pyramid_swagger.schema_directory'] = os.path.join(
        os.path.dirname(__file__),
        'swagger'
    )
    settings['pyramid_swagger.schema_file'] = 'api.yml'

    config.include('pyramid_swagger')

    config.include('iris.service.sms.sms')
    config.include('iris.service.db')
    config.include('iris.service.cors')
    config.include('iris.service.rest')
    config.include('iris.service.rest.service')
    config.include('iris.service.endpoint')
    config.include('iris.service.swaggerui')
    config.include('iris.service.static')
    config.include('iris.service.og',
                   route_prefix=API_V1_BASE_URL)
    config.include('iris.service.content.file',
                   route_prefix=API_V1_BASE_URL)
    config.include('iris.service.content.file.s3')
    config.include('iris.service.content.weblocation',
                   route_prefix=API_V1_BASE_URL)
    config.include('iris.service.content.petition',
                   route_prefix=API_V1_BASE_URL)
    config.include('iris.service.content.petition.sm')
    config.include('iris.service.content.user',
                   route_prefix=API_V1_BASE_URL)
    config.include('iris.service.content.city',
                   route_prefix=API_V1_BASE_URL)
    config.include('iris.service.content.confirmation',
                   route_prefix=API_V1_BASE_URL)
    config.include('iris.service.auth',
                   route_prefix=API_V1_BASE_URL)
    config.include('iris.service.sm',
                   route_prefix=API_V1_BASE_URL)
    config.include('iris.service.security.policy')
    config.include('iris.service.auth.sso')

    config.scan('iris.service.cors')
    config.scan('iris.service.rest')
    config.scan('iris.service.rest.service')
    config.scan('iris.service.swaggerui')
    config.scan('iris.service.static')
    config.scan('iris.service.og')
    config.scan('iris.service.content.weblocation')
    config.scan('iris.service.content.file')
    config.scan('iris.service.content.petition')
    config.scan('iris.service.content.user')
    config.scan('iris.service.content.city')
    config.scan('iris.service.content.confirmation')
    config.scan('iris.service.auth')
    config.scan('iris.service.sm')
    config.scan('iris.service.auth.sso')

    return config.make_wsgi_app()
