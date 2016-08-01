from pyramid.view import view_config


@view_config(route_name='login_embed',
             request_method='GET',
             renderer='templates/login_embed.jinja2'
            )
def login_embed(request):
    request.response.content_type = 'application/javascript'
    return {
        'apiBasePath': request.application_url,
    }
