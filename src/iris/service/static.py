from pyramid.httpexceptions import HTTPFound
from pyramid.config import aslist
from pyramid.view import view_config


def staticRedirectView(request):
    if request.path.endswith('swagger'):
        # Provide the swagger spec file
        return HTTPFound(request.path + '/?url=/swagger.json')
    return HTTPFound(request.path + '/')


def includeme(config):
    settings = config.get_settings()
    for key, value in settings.iteritems():
        if not key.startswith('static.'):
            continue
        path, url = aslist(value)
        config.add_static_view(name=url, path=path)
        view_config(route_name=key)(staticRedirectView)
        config.add_route(key, url)
