from pyramid.view import view_config


@view_config(route_name='sample', renderer='json')
def sample_view(request):
    return {"hello": "blub!"}


def includeme(config):
    config.add_route('sample', '/sample')
