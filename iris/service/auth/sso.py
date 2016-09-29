import logging
import time
import hashlib
import hmac
import base64
import json
import jsonschema

from iris.service.content.user import User
from iris.service.security.security import session_user, login_user

from .ssotoken import SSOToken

logger = logging.getLogger(__name__)


def _sso_data(request):
    """Get sso data from the request

    SSO data can be provided using 'sso' or 'token' parameter via
    swagger_data. If one of these parameters is provided 'apikey' must also be
    in swagger_data.

    If the 'token' is provided the token is expanded into the sso data. The
    token is no longer valid after the call to this method.
    """
    sso = request.swagger_data.get('sso')
    token = request.swagger_data.get('token')
    if (sso is None) == (token is None):
        return None
    if token is not None:
        # resolve the token
        data = SSOToken.resolve(token)
        if data is None:
            return None
        sso, apikey = data
    else:
        # the apikey must be provided by the request
        apikey = request.swagger_data.get('apikey')
        if apikey is None:
            return None
    try:
        verify_message(sso, apikey)
    except (ValueError, KeyError):
        return None
    return {
        'data': get_message_data(sso),
        'apikey': apikey
    }


def _user(request):
    """The request method to get the user from the current request

    Is used for the request method `request.user`.
    """
    user_id = request.authenticated_userid
    if not user_id:
        return None
    return session_user(user_id) or User.get(user_id)


def _session_user(request):
    """The request method to get the user from the current request

    The difference to the _user method is that a SessionUser is returned if no
    authentication is available.
    """
    user = request.user
    if user:
        return user
    login_user(request, request.response)
    return request.user


def get_or_create_sso_user(ssodata):
    """Get or create a user based on SSO credentials

    The SSO credentials are a dict providing the properties defined in
    SSO_USER_SCHEMA below.
    """
    data = ssodata.get('data')
    if not data:
        return None
    try:
        jsonschema.validate(data, SSO_USER_SCHEMA)
    except jsonschema.exceptions.ValidationError:
        return None
    user_properties = {
        'sso': {
            'provider': ssodata['apikey']
        },
    }
    for name in SSO_USER_SCHEMA['properties'].keys():
        value = data.get(name)
        if value:
            user_properties[name] = value
    return User.update_or_create_by_email(**user_properties)


SSO_USER_SCHEMA = {
    'type': 'object',
    'required': ['email'],
    'properties': {
        'email': {
            'type': 'string',
        },
        'email_trusted': {
            'type': 'boolean',
        },
        'mobile': {
            'type': 'string',
        },
        'mobile_trusted': {
            'type': 'boolean',
        },
        'firstname': {
            'type': 'string',
        },
        'lastname': {
            'type': 'string',
        },
        'street': {
            'type': 'string',
        },
        'zip': {
            'type': 'string',
        },
        'town': {
            'type': 'string',
        },
        'roles': {
            'type': 'array',
            'items': {
                'type': 'string',
            }
        },
    }
}


PRIVATE_KEYS = {}

SIG_EXPIRATION = 2 * 60 * 60  # seconds


def verify_message(msg, api_key):
    """Accepts a string which is a signed HMAC (see 'sign_message').

    The 'msg' consists of three parts:
        - base64 encoded JSON data
        - signed JSON data (signed with a shared secret and a timestamp)
        - timestamp
    The parts have to be concatenated with ', '. The blank space is important.
    A message older than 2 hours will be marked as invalid

    Raises a ValueError error or returns True.
    """
    parts = msg.split(', ')
    if not parts or len(parts) != 3:
        logger.error(
            "Invalid sso parts : '{0}', 'api_key': '{1}'".format(
                msg, api_key))
        raise ValueError('Invalid sso data')
    message, remote_sig, ts = parts
    shared_secret = get_private_key(api_key)
    our_sig = hmac.new(shared_secret,
                       '{m} {ts}'.format(m=message, ts=ts),
                       hashlib.sha1).hexdigest()
    if remote_sig != our_sig:
        logger.error(
            "Invalid sso signature : '{0}', 'api_key': '{1}'".format(
                msg, api_key))
        raise ValueError('Invalid sso data')
    if int(ts) <= (int(time.time()) - SIG_EXPIRATION):
        logger.error(
            "sso expired : '{0}', 'api_key': '{1}'".format(
                msg, api_key))
        raise ValueError('Invalid sso data')
    return True


def get_message_data(msg):
    """Extracts the message data from the sso message

    Note: the message is not verified here!
    """
    return json.loads(base64.b64decode(msg.split(', ')[0]))


def get_private_key(api_key):
    """Get the private key for the public api key

    raises a KeyError if the api_key doesn't exist.
    """
    return PRIVATE_KEYS[api_key]


def sign_message(data, api_key):
    """Create a signed message

    This is only required for testing.
    """
    dataJson = json.dumps(data)
    message = base64.b64encode(dataJson)
    timestamp = int(time.time())
    shared_secret = get_private_key(api_key)
    sig = hmac.new(shared_secret,
                   '{m} {ts}'.format(m=message, ts=timestamp),
                   hashlib.sha1).hexdigest()
    return '{m}, {sig}, {ts}'.format(m=message, sig=sig, ts=timestamp)


def includeme(config):
    global PRIVATE_KEYS
    settings = config.get_settings()
    for key, value in settings.iteritems():
        if not key.startswith('sso.apikey.'):
            continue
        public = key[11:]
        PRIVATE_KEYS[public] = value
        logger.info('loaded sso api-key for "%s"', public)
    config.add_request_method(_sso_data, "sso_data")
    config.add_request_method(_user, "user", reify=True)
    config.add_request_method(_session_user, "session_user", reify=True)
