import json
import logging

import WebSmsComToolkit


logger = logging.getLogger(__name__)


SMS_PROVIDER_URI = None
SMS_CLIENT_CONFIG = {}
TESTING = False

TEST_STACK = []


def sendSMS(to, message):
    global SMS_CLIENT_CONFIG, SMS_PROVIDER_URI
    if TESTING or to.startswith('555'):
        if to == '555 333':
            # simulate a value error for testing
            raise ValueError("Can't send SMS")
        TEST_STACK.append([to, message])
        print 'sendSMS(%r, %r)' % (to, message)
        return {}

    if isinstance(message, str):
        message = unicode(message, 'utf-8')
    to = to.replace(' ', '')
    client = WebSmsComToolkit.Client(**SMS_CLIENT_CONFIG)
    message = WebSmsComToolkit.TextMessage([long(to)], message)
    try:
        response = client.send(message, 1, False)
    except Exception as e:
        logger.error(e)
        raise ValueError("Can't send SMS")
    if response.statusMessage != u'OK':
        logger.error(json.dumps(response.rawContent))
        raise ValueError("Can't send SMS: " + response.statusMessage)
    logger.info(json.dumps(response.rawContent))
    return response.rawContent


def includeme(config):
    global SMS_CLIENT_CONFIG, SMS_PROVIDER_URI, TESTING
    settings = config.get_settings()
    for key, value in settings.iteritems():
        if key.startswith('sms.client.'):
            SMS_CLIENT_CONFIG[key[11:]] = value
    SMS_PROVIDER_URI = settings.get('sms.uri')
    if not SMS_CLIENT_CONFIG:
        TESTING = True
    else:
        TESTING = 'sms.testing' in settings
