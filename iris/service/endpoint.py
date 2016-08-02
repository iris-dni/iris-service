import traceback

from .errors import Errors


class BadRequest(Exception):
    """Used as a response in case of an error

    A response handler exists to render a proper JSON response body.
    """

    def __init__(self,
                 error_code,
                 http_status=400,
                 replacements={}):
        self.http_status = http_status
        self.replacements = replacements
        super(BadRequest, self).__init__(error_code)


class EndpointErrorMixin(object):
    """A mixin for endpoints for a simple error handling
    """

    ERROR_CODES = []

    def bad_request(self, error_code=None, replacements={}):
        if error_code is None:
            error_code = Errors.bad_request
        self.check_valid_code(error_code)
        return BadRequest(error_code, replacements=replacements)

    def unauthenticated(self, error_code=None, replacements={}):
        if error_code is None:
            error_code = Errors.unauthenticated
        self.check_valid_code(error_code)
        return BadRequest(error_code,
                          http_status=401,
                          replacements=replacements)

    def forbidden(self, error_code=None, replacements={}):
        if error_code is None:
            error_code = Errors.forbidden
        self.check_valid_code(error_code)
        return BadRequest(error_code,
                          http_status=403,
                          replacements=replacements)

    def not_found(self, error_code=None, replacements={}):
        if error_code is None:
            error_code = Errors.not_found
        self.check_valid_code(error_code)
        return BadRequest(error_code,
                          http_status=404,
                          replacements=replacements)

    def method_not_allowed(self, error_code=None, replacements={}):
        if error_code is None:
            error_code = Errors.method_not_allowed
        self.check_valid_code(error_code)
        return BadRequest(error_code,
                          http_status=405,
                          replacements=replacements)

    def check_valid_code(self, code):
        return
        if code not in self.ERROR_CODES:
            # This is a check to make sure no error code is provided which is
            # not added to the documentation.

            raise ValueError(
                'Error Code "%s" not defined for the endpoint' % code
            )


def bad_request_handler(exc, request):
    """Handles response BadRequest

    Renders a proper json response
    """
    request.response.status = exc.http_status
    return {
        'error': {
            'code': exc.http_status,
            'description': exc.message.value.format(**exc.replacements),
        }
    }


def exc_response(exc, request, with_traceback=False):
    result = {
        'errors': {
            'code': str(exc.code),
            'description': exc.detail,
        }
    }
    if with_traceback:
        result['errors']['traceback'] = traceback.format_exc(exc)
    return result


def http_4xx(exc, request):
    """Handle all HTTP client errors (status-code 4xx)
    """
    request.response.status = exc.code
    return exc_response(exc, request)


def http_5xx(exc, request):
    """Handle all HTTP server errors (status-code 5xx)
    """
    request.response.status = exc.code
    return exc_response(exc, request, True)


def includeme(config):
    config.add_view(
        bad_request_handler,
        renderer='json',
        context=BadRequest,
        http_cache=0,
    )
    config.add_view(
        http_4xx,
        renderer='json',
        context='pyramid.httpexceptions.HTTPClientError',
        http_cache=0,
    )
    config.add_view(
        http_5xx,
        renderer='json',
        context='pyramid.httpexceptions.HTTPServerError',
        http_cache=0,
    )
