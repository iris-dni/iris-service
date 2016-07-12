from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config


@view_config(route_name='docs')
def docsRedirectView(request):
    return HTTPFound('/docs/')


def includeme(config):
    settings = config.get_settings()
    docsPath = settings.get('docs.path', 'iris.service:docs')
    config.add_static_view(name='/docs', path=docsPath)
    config.add_route('docs', '/docs')
