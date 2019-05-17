=====================
Single Sign On Secret
=====================


Private Secret
==============

API keys are defined in the pyramid settings file in the form::

    sso.apikey.<public_key> = <private_key>

Now the private key can be accessed via the public key::

    >>> from iris.service.auth.sso import get_private_key
    >>> get_private_key('test_public_api_key')
    'test_private_api_key'

    >>> get_private_key('unknown_public_api_key')
    Traceback (most recent call last):
    KeyError: 'unknown_public_api_key'


SSO Message Verification
========================

SSO messages are secured using a signature. Each SSO message must be verfied
before it can be used.

First we need to create a signed SSO message::

    >>> from iris.service.auth.sso import sign_message
    >>> message = sign_message({'some': 'data'}, 'test_public_api_key')

Now the message can be verified::

    >>> from iris.service.auth.sso import verify_message

    >>> verify_message(message, 'test_public_api_key')
    True

With a wrong public key we get an error::

    >>> verify_message(message, 'other_public_api_key')
    Traceback (most recent call last):
    ValueError: Invalid sso data

With an unknown public key we get an error::

    >>> verify_message(message, 'unknown_public_api_key')
    Traceback (most recent call last):
    KeyError: 'unknown_public_api_key'

Change parts of the message::

    >>> invalid_msg = message + '-'
    >>> verify_message(invalid_msg, 'test_public_api_key')
    Traceback (most recent call last):
    ValueError: Invalid sso data

Signatures expire after a certain time::

    >>> from iris.service.auth import sso
    >>> sso.SIG_EXPIRATION   # in seconds
    7200

For testing purposes, we reduce this time::

    >>> sso.SIG_EXPIRATION = 1   # second
    >>> import time
    >>> time.sleep(1)
    >>> sso.verify_message(message, 'test_public_api_key')
    Traceback (most recent call last):
    ValueError: Invalid sso data

Invalid message format::

    >>> sso.verify_message('lorem ipsum', 'test_public_api_key')
    Traceback (most recent call last):
    ValueError: Invalid sso data


Message Data Extraction
=======================

The data can be extracted from the message::

    >>> from iris.service.auth.sso import get_message_data

    >>> get_message_data(message)
    {u'some': u'data'}
