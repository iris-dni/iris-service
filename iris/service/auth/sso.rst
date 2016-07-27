===========
SSO Methods
===========

The request provides the property 'sso_data' with which the data can be
extracted from the sso query parameters provided in request.swagger_data.

The method implementation is here::

    >>> from iris.service.auth.sso import _sso_data
    >>> request = get_test_request()


Using SSO Message
=================

We need a signed sso message::

    >>> from iris.service.auth.secret import sign_message
    >>> message = sign_message({'some': 'data'}, 'test_public_api_key')

Put the data into swagger_data::

    >>> request.swagger_data = {'sso': message, 'apikey': 'test_public_api_key'}

Now the data can be extracted::

    >>> pp(_sso_data(request))
    {
      "some": "data"
    }

Without any parameters::

    >>> request.swagger_data = {}
    >>> _sso_data(request) is None
    True

With a missing apikey::

    >>> request.swagger_data = {'sso': message}
    >>> _sso_data(request) is None
    True

With a wrong apikey::

    >>> request.swagger_data = {'sso': message, 'apikey': 'other_public_api_key'}
    >>> _sso_data(request) is None
    True


Using a Token
=============

Create a token::

    >>> from iris.service.auth import SSOToken
    >>> token = SSOToken(sso=message, apikey='test_public_api_key')
    >>> _ = token.store()

    >>> request.swagger_data = {'token': token.token}
    >>> pp(_sso_data(request))
    {
      "some": "data"
    }

The token is no longer available::

    >>> SSOToken.get(token.token) is None
    True

With a not existing token::

    >>> request.swagger_data = {'token': token.token}
    >>> _sso_data(request) is None
    True


Get/Create User from SSO Data
=============================

User access via sso data requires at least the email::

    >>> from iris.service.auth.sso import get_or_create_sso_user
    >>> get_or_create_sso_user({}) is None
    True

With valid data::

    >>> u1 = get_or_create_sso_user({'email': 'my_1@mail.com'})
    >>> u1
    <User [id=1, 'my_1@mail.com']>
    >>> u2 = get_or_create_sso_user({
    ...     'email': 'my_2@mail.com',
    ...     'firstname': 'first',
    ...     'lastname': 'last',
    ...     'trusted': True,
    ...     'roles': ['admin', 'editor'],
    ... })
    >>> u2
    <User [id=2, 'my_2@mail.com']>
    >>> u2.firstname, u2.lastname
    ('first', 'last')
    >>> u2.trusted
    True
    >>> u2.roles
    ['admin', 'editor', 'trusted']

    >>> from iris.service.user import User
    >>> User.get(u1.id)
    <User [id=1, u'my_1@mail.com']>
    >>> User.get(u2.id)
    <User [id=2, u'my_2@mail.com']>

There is no error if more data is provided::

    >>> u3 = get_or_create_sso_user({
    ...     'email': 'my_3@mail.com',
    ...     'additional_property': 'more',
    ... })
    >>> u3
    <User [id=3, 'my_3@mail.com']>
