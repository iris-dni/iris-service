from pyramid.view import view_config
from pyramid.response import Response


RESPONSE_BODY = u"OK"


@view_config(route_name='probe_status')
def probe_status_view(request):
    """probe status endpoint

    This endpoint allows to check if the service is available and to
    decommission the service.

    Decommissioning can be used to make the service unavailable for load
    balancers before the service is shut down.
    """
    global RESPONSE_BODY
    response = Response()
    response.content_type = 'text/plain'
    if request.method == 'POST':
        RESPONSE_BODY = request.GET.get('body', u'OK')
    else:
        if RESPONSE_BODY != "OK":
            response.status = 503
    response.text = RESPONSE_BODY
    return response


def includeme(config):
    config.add_route('probe_status', '/probe_status')
