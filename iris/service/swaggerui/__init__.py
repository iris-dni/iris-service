from pyramid.view import view_config


def swaggerUIView(request):
    # TODO: disable everything for none admins except get and options
    return {
        'supportedSubmitMethods': [
            'get', 'options', 'post', 'put', 'delete', 'patch'
        ],
    }


def includeme(config):
    """Setup swagger ui

    swagger_ui.url: URL at which the swagger ui should be accessable
                    swagger-ui will not be available if not provided or empty
    """
    settings = config.get_settings()
    swagger_url = settings.get('swagger_ui.url')
    if swagger_url:
        view_config(route_name='swagger-ui',
                    renderer='index.jinja2'
                   )(swaggerUIView)
        config.add_route('swagger-ui', swagger_url)
        config.add_static_view(name='/%s_resources/' % swagger_url,
                               path='iris.service:swaggerui/dist')
