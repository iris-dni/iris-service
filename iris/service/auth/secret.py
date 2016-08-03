import logging
import time
import hashlib
import hmac
import base64
import json

logger = logging.getLogger(__name__)


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
