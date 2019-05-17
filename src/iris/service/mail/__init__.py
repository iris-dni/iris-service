import logging
import json

import mandrill


log = logging.getLogger(__name__)


CLIENT = None
SETTINGS = {}


def send(name, to, data):
    """Send a mail using mandrill

    `name` is the mandrill template name to use
    `to` is a list of receipients as an object:
        {
          "mail": "<user email>",
          "firstname": "<optional>",
          "lastname": "<optional>"
        }
    `data` contains the vars which the template can use

    The `data` is always extended with `portal` data:
        "portal": {
          "url": "<portal URL>"
        }
    """
    extend_with_portal(data)

    def prepare_to(user):
        result = {
            'email': user['email'],
            'type': 'to',
        }
        fn = user.get('firstname', '')
        ln = user.get('lastname', '')
        if fn or ln:
            result['name'] = fn + ' ' + ln
        return result
    params = {
        'template_name': name,
        'template_content': [],
        'message': {
            'to': [prepare_to(d) for d in to],
            'global_merge_vars': flatten_vars(data),
            'merge_vars': [
                {
                    'rcpt': r['email'],
                    'vars': flatten_vars({'user': r})
                } for r in to
            ]
        },
    }
    log.info(json.dumps(params, sort_keys=True))
    result = None
    try:
        result = CLIENT.messages.send_template(**params)
        for status in result:
            log.info(json.dumps(status, sort_keys=True))
    except mandrill.Error as e:
        log.error('mail send error: %s - %s', e.__class__, e)
    return result


def extend_with_portal(data):
    """add "portal" data to `data`
    """
    portal = data.setdefault("portal", {})
    portal.update(SETTINGS['domain'])


def flatten_vars(data):
    """Flatten data and provide it as a var list

    The result list is sorted maily for debuging and tests.
    """
    return sorted([
            {
                'name': k,
                'content': v
            } for k, v in data.items()
        ],
        key=lambda d: d['name'],
    )


TESTING_MAIL_STACK = []


def reset_mail_stack():
    TESTING_MAIL_STACK[:] = []


def includeme(config):
    global CLIENT
    settings = config.get_settings()
    key = settings.get('mandrill.key')
    if key == 'mock':
        class mandrill_mock_messages(object):
            def send_template(*args, **kwargs):
                TESTING_MAIL_STACK.append(kwargs)
                return {}

        class mandrill_mock_client(object):
            messages = mandrill_mock_messages()
        CLIENT = mandrill_mock_client()
    elif key:
        CLIENT = mandrill.Mandrill(key)
    global SETTINGS
    mail = SETTINGS['domain'] = {}
    mail['url'] = settings.get('frontend.domain')
