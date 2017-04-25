import json
import logging

import twitter

from jinja2 import Template


log = logging.getLogger(__name__)


API_PARAMS = {}

TEMPLATES = {}

API = twitter.Api


def send(name, data):
    """Send a message to twitter

    `name` is the jinja template name to use
    `data` is the context provided to the jinja template, this should be the
           same data as it is used for mails.
    """
    message = renderMessage(name, data)
    if message is None:
        log.error('Twitter template "%s" not found' % name)
        return
    params = {
        "PostUpdate": {
            "status": message
        },
        "template": TEMPLATES[name],
        "data": data
    }
    log.info(json.dumps(params, sort_keys=True))
    api = API(**API_PARAMS)
    result = api.PostUpdate(**params['PostUpdate'])
    log.info(json.dumps(result, sort_keys=True))
    return result


def renderMessage(name, data):
    if name not in TEMPLATES:
        return None
    template = Template(TEMPLATES[name])
    return template.render(**data)


def includeme(config):
    global API_PARAMS, API
    settings = config.get_settings()
    for key, value in settings.iteritems():
        if key.startswith('twitter.api.'):
            API_PARAMS[key[12:]] = unicode(value, 'utf-8')
        elif key.startswith('twitter.template.'):
            TEMPLATES[key[17:]] = unicode(value, 'utf-8')
    if 'mock' in API_PARAMS:
        from .testing import TwitterMock
        API = TwitterMock()
        del API_PARAMS['mock']
