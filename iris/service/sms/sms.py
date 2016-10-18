import boto3
from botocore.exceptions import ClientError


AWS_CLIENT_CONFIG = {}
AWS_PUBLISH_CONFIG = {}
TESTING = False


def sendSMS(to, subject, message):
    global AWS_CLIENT_CONFIG, AWS_PUBLISH_CONFIG
    if TESTING or to.startswith('555'):
        if to == '555 333':
            # simulate a value error for testing
            raise ValueError("Can't send SMS")
        print 'sendSMS(%r, %r, %r)' % (to, subject, message)
        return {}
    client = boto3.client(
        'sns',
        **AWS_CLIENT_CONFIG
    )
    try:
        return client.publish(
            PhoneNumber=to,
            Message=message,
            Subject=subject,
            **AWS_PUBLISH_CONFIG
        )
    except ClientError:
        raise ValueError("Can't send SMS")


def includeme(config):
    global AWS_CLIENT_CONFIG, AWS_PUBLISH_CONFIG, TESTING
    settings = config.get_settings()
    for key, value in settings.iteritems():
        if key.startswith('aws.sns.publish.'):
            AWS_PUBLISH_CONFIG[key[16:]] = value
        elif key.startswith('aws.sns.'):
            AWS_CLIENT_CONFIG[key[8:]] = value
    if not AWS_CLIENT_CONFIG and not AWS_PUBLISH_CONFIG:
        TESTING = True
    else:
        TESTING = 'aws.testing' in settings
