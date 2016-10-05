import boto3


AWS_CLIENT_CONFIG = {}
AWS_PUBLISH_CONFIG = {}
TESTING = False


def sendSMS(to, subject, message):
    global AWS_CLIENT_CONFIG, AWS_PUBLISH_CONFIG
    if TESTING or to.startswith('555'):
        print 'sendSMS(%r, %r, %r)' % (to, subject, message)
        return {}
    client = boto3.client(
        'sns',
        **AWS_CLIENT_CONFIG
    )
    return client.publish(
        PhoneNumber=to,
        Message=message,
        Subject=subject,
        **AWS_PUBLISH_CONFIG
    )


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
