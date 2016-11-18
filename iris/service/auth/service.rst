============
Auth Service
============

    >>> from iris.service.auth.sso import sign_message
    >>> # sign_message({'email': 'me@you.com', 'roles': ['admin']}, 'local')


Check Current Login
===================

The whoami endpoint provides the data of the currently logged in user::

    >>> response = browser.get('/v1/auth/whoami', expect_errors=True)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "status": "unauthenticated"
    }


SSO Login
=========

The sso or token parameter is required::

    >>> response = browser.post('/v1/auth/ssologin', expect_errors=True)
    >>> response.status
    '400 Bad Request'
    >>> print_json(response)
    {
      "error": {
        "code": 400,
        "description": "No parameters provided"
      }
    }

    >>> response = browser.post('/v1/auth/ssologin?sso=123&token=321', expect_errors=True)
    >>> response.headers['cache-control']
    'max-age=0, must-revalidate, no-cache, no-store'
    >>> response.headers['pragma']
    'no-cache'
    >>> response.headers['expires']
    '... GMT'
    >>> response.headers['last-modified']
    '... GMT'
    >>> response.status
    '400 Bad Request'
    >>> print_json(response)
    {
      "error": {
        "code": 400,
        "description": "Too many parameters provided"
      }
    }

Login with sso data::

    >>> message = sign_message(
    ...     {
    ...         'email': 'me-sso@you.com',
    ...         'firstname': 'hoschi',
    ...         'roles': ['admin'],
    ...     },
    ...     'test_public_api_key',
    ... )
    >>> response = browser.post('/v1/auth/ssologin?sso=%s&apikey=test_public_api_key' % message)
    >>> print_json(response)
    {
      "data": {
        ...
        "email": "me-sso@you.com",
        ...
      },
      "status": "ok"
    }

Logout an sso user with an empty object::

    >>> message = sign_message(
    ...     {},
    ...     'test_public_api_key',
    ... )
    >>> response = browser.post('/v1/auth/ssologin?sso=%s&apikey=test_public_api_key' % message, expect_errors=True)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "status": "unauthenticated"
    }

Logout is performed if email is missing::

    >>> message = sign_message(
    ...     {
    ...         'lastname': 'last'
    ...     },
    ...     'test_public_api_key',
    ... )
    >>> response = browser.post('/v1/auth/ssologin?sso=%s&apikey=test_public_api_key' % message, expect_errors=True)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "status": "unauthenticated"
    }


SSO Token
=========

We need a valid sso message::

    >>> message = sign_message(
    ...     {
    ...         'email': 'me@you.com',
    ...         'firstname': 'hoschi',
    ...         'roles': ['admin'],
    ...     },
    ...     'test_public_api_key',
    ... )

To transfer a login from one domain to another an SSO token must be
requested::

    >>> response = browser.post('/v1/auth/ssotoken'
    ...                         '?sso=%s'
    ...                         '&apikey=test_public_api_key' % message)
    >>> print_json(response)
    {
      "token": "2688dba5a677a8c704f1ed1e248bf526"
    }

    >>> token = response.json['token']

The ssologin endpoint can use the token to login::

    >>> response = browser.post('/v1/auth/ssologin?token=%s' % token)
    >>> print_json(response)
    {
      ...
      "email": "me@you.com",
      ...
      "firstname": "hoschi",
      ...
        "roles": [
          "admin"
        ],
      ...
    }
    >>> response = browser.get('/v1/auth/whoami')
    >>> print_json(response)
    {
      ...
      "email": "me@you.com",
      ...
    }

It can be used multiple times on the same user::

    >>> response = browser.post('/v1/auth/ssotoken'
    ...                         '?sso=%s'
    ...                         '&apikey=test_public_api_key' % message)
    >>> token = response.json['token']
    >>> response = browser.post('/v1/auth/ssologin?token=%s' % token)
    >>> print_json(response.headerlist)
    [
      ...
      [
        "Set-Cookie",
        "iris-tkt=\"...!userid_type:b64unicode\"; Path=/"
      ],
    ...
    >>> print_json(response)
    {
      ...
      "email": "me@you.com",
      ...
    }

The sso parameter is required::

    >>> response = browser.post('/v1/auth/ssotoken', expect_errors=True)
    >>> response.status
    '400 Bad Request'
    >>> print_json(response)
    {
      "errors": {
        "code": "400",
        "description": "sso is a required parameter..."
      }
    }
    >>> print_json({n: v for n,v in response.headers.items()})
    {
      "Access-Control-Allow-Credentials": "true",
      "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization",
      "Access-Control-Allow-Methods": "POST,GET,DELETE,PUT,OPTIONS",
      "Access-Control-Allow-Origin": "http://localhost",
      "Access-Control-Max-Age": "86400",
      ...


Logout
======

The user can be logged out::

    >>> response = browser.post('/v1/auth/logout')
    >>> print_json(response)
    {}


Whoami With SSO Data
====================

whoami can be used to check sso data.

sso with apikey::

    >>> message = sign_message({'email': 'me_check@you.com','firstname': 'me'}, 'test_public_api_key')

    >>> response = browser.get('/v1/auth/whoami?sso=%s&apikey=test_public_api_key' % message)
    >>> print_json(response)
    {
      "data": {
        "dc": {
          "created": "...",
          "modified": "..."
        },
        "email": "me_check@you.com",
        "email_trusted": false,
        "firstname": "me",
        "id": ...,
        "lastname": "",
        "mobile": "",
        "mobile_trusted": false,
        "roles": [],
        "salutation": "",
        "sso": [
          {
            "provider": "test_public_api_key"
          }
        ],
        "state": "active",
        "street": "",
        "town": "",
        "zip": ""
      },
      "status": "ok"
    }

When using a token the user is logged in the same way as she would be logged
in the ssologin endpoint::

    >>> message = sign_message({'email': 'me_check@you.com','lastname': 'me last'}, 'test_public_api_key')
    >>> response = browser.post('/v1/auth/ssotoken'
    ...                         '?sso=%s'
    ...                         '&apikey=test_public_api_key' % message)
    >>> token = response.json['token']
    >>> response = browser.get('/v1/auth/whoami?token=%s' % token)
    >>> print_json(response.headerlist)
    [
      ...
      [
        "Set-Cookie",
        "iris-tkt=\"...!userid_type:b64unicode\"; Path=/"
      ],
    ...
    >>> print_json(response)
    {
      "data": {
        "dc": {
          "created": "...",
          "modified": "..."
        },
        "email": "me_check@you.com",
        "email_trusted": false,
        "firstname": "me",
        "id": ...,
        "lastname": "me last",
        "mobile": "",
        "mobile_trusted": false,
        "roles": [],
        "salutation": "",
        "sso": [
          {
            "provider": "test_public_api_key"
          }
        ],
        "state": "active",
        "street": "",
        "town": "",
        "zip": ""
      },
      "status": "ok"
    }
