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

    >>> from iris.service.auth.sso import sign_message
    >>> message = sign_message({'some': 'data'}, 'test_public_api_key')

Put the data into swagger_data::

    >>> request.swagger_data = {'sso': message, 'apikey': 'test_public_api_key'}

Now the data can be extracted::

    >>> pp(_sso_data(request))
    {
      "apikey": "test_public_api_key",
      "data": {
        "some": "data"
      }
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
      "apikey": "test_public_api_key",
      "data": {
        "some": "data"
      }
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

    >>> u1 = get_or_create_sso_user({
    ...     'data': {
    ...         'email': 'my_1@mail.com'
    ...     },
    ...     'apikey': '42'
    ... })
    >>> u1
    <User [id=u'1n3gf', 'my_1@mail.com']>
    >>> u1.sso
    [{'trusted': False, 'provider': '42'}]
    >>> u2 = get_or_create_sso_user({
    ...     'data': {
    ...         'email': 'my_2@mail.com',
    ...         'firstname': 'first',
    ...         'lastname': 'last',
    ...         'trusted': True,
    ...         'roles': ['admin', 'editor'],
    ...     },
    ...     'apikey': '42'
    ... })
    >>> u2
    <User [id=u'1Zbfk', 'my_2@mail.com']>
    >>> u2.firstname, u2.lastname
    ('first', 'last')
    >>> u2.roles
    ['admin', 'editor']
    >>> u2.sso
    [{'trusted': True, 'provider': '42'}]

    >>> from iris.service.content.user import User
    >>> User.get(u1.id)
    <User [id=u'1n3gf', u'my_1@mail.com']>
    >>> User.get(u2.id)
    <User [id=u'1Zbfk', u'my_2@mail.com']>

There is no error if more data is provided::

    >>> u3 = get_or_create_sso_user({
    ...     'data': {
    ...         'email': 'my_3@mail.com',
    ...         'additional_property': 'more',
    ...     },
    ...     'apikey': '42'
    ... })
    >>> u3
    <User [id=u'1QjR3', 'my_3@mail.com']>

Update an existing user::

    >>> u2 = get_or_create_sso_user({
    ...     'data': {
    ...         'email': 'my_2@mail.com',
    ...         'firstname': 'second',
    ...         'trusted': False,
    ...     },
    ...     'apikey': '42'
    ... })
    >>> u2.firstname, u2.lastname
    ('second', u'last')
    >>> u2.sso
    [{u'trusted': False, u'provider': '42'}]
    >>> u2.roles
    [u'admin', u'editor']
