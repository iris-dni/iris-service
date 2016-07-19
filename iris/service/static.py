from pyramid.httpexceptions import HTTPFound
from pyramid.config import aslist
from pyramid.view import view_config


def staticRedirectView(request):
    return HTTPFound(request.path + '/')


def includeme(config):
    settings = config.get_settings()
    for key, value in settings.iteritems():
        if not key.startswith('static.'):
            continue
        path, url = aslist(value)
        view_config(route_name=key)(staticRedirectView)
        config.add_static_view(name=key[7:] + '/', path=path)
        config.add_route(key, url)
