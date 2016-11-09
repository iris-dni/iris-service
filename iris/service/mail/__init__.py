import logging
import json

import mandrill


log = logging.getLogger(__name__)


CLIENT = None


def send(name, to, data):
    """Send a mail using mandrill
    """
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
    log.info(json.dumps(params), sort_keys=True)
    result = None
    try:
        result = CLIENT.messages.send_template(**params)
        for status in result:
            log.info(json.dumps(status, sort_keys=True))
    except mandrill.Error as e:
        log.error('mail send error: %s - %s', e.__class__, e)
    return result


def flatten_vars(data):
    """Flatten data and provide it as a var list

    The result list is sorted maily for debuging and tests.
    """
    return sorted([
            {
                'name': k,
                'content': v
            } for k, v in flatten_dict(data).items()
        ],
        key=lambda d: d['name'],
    )


def flatten_dict(data, leading=''):
    """Flatten out nested dicts to build the variable names for mandrill
    """
    result = {}
    for k, v in data.items():
        if leading:
            name = leading + '_' + k
        else:
            name = k
        if isinstance(v, dict):
            result.update(flatten_dict(v, name))
        else:
            result[name] = v
    return result


def includeme(config):
    global CLIENT
    settings = config.get_settings()
    key = settings.get('mandrill.key')
    if key == 'mock':
        class mandrill_mock_messages(object):
            def send_template(*args, **kwargs):
                from pprint import pprint
                pprint(kwargs)
                return {}

        class mandrill_mock_client(object):
            messages = mandrill_mock_messages()
        CLIENT = mandrill_mock_client()
    elif key:
        CLIENT = mandrill.Mandrill(key)
