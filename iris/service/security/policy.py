import logging

from pyramid.authentication import (
    AuthTktAuthenticationPolicy,
    AuthTktCookieHelper,
)

from . import acl


logger = logging.getLogger(__name__)


API_KEY_HEADER_NAME = 'X-Iris-Api-Key'

API_KEYS = set([])


class IRISAuthTktCookieHelper(AuthTktCookieHelper):
    """Used to be able to login via an API key defined in the request header

    """

    def identify(self, request):
        global API_KEYS
        apikey = request.headers.get(API_KEY_HEADER_NAME)
        if apikey is not None:
            if apikey in API_KEYS:
                # provide a userid which can be handled in the groupfinder
                return {
                    "userid": acl.Roles.ApiKeyUser
                }
            # invalid api key
            return None
        return super(IRISAuthTktCookieHelper, self).identify(request)


class IRISAuthPolicy(AuthTktAuthenticationPolicy):
    """An authentication policy which checks for an API key header
    """

    def __init__(self, *args, **kwargs):
        super(IRISAuthPolicy, self).__init__(*args, **kwargs)
        # init cookie helper and remove unexpected keywords
        if 'callback' in kwargs:
            del kwargs['callback']
        self.cookie = IRISAuthTktCookieHelper(*args, **kwargs)


def includeme(config):
    global API_KEYS
    settings = config.get_settings()
    for key, value in settings.iteritems():
        if not key.startswith('iris.apikey.'):
            continue
        name = key[12:]
        API_KEYS.add(value)
        logger.info('loaded iris api-key for "%s"', name)
