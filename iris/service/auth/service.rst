============
Auth Service
============


Check Current Login
===================

The whoami endpoint provides the data of the currently logged in user::

    >>> response = browser.get('/v1/auth/whoami', expect_errors=True)
    >>> response.status
    '400 Bad Request'
    >>> print_json(response)
    {
      "error": {
        "code": 400,
        "description": "Not logged in"
      }
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
    >>> response.status
    '400 Bad Request'
    >>> print_json(response)
    {
      "error": {
        "code": 400,
        "description": "Too many parameters provided"
      }
    }


SSO Token
=========

We need a valid sso message::

    >>> from iris.service.auth.secret import sign_message
    >>> message = sign_message({'email': 'me@you.com'}, 'test_public_api_key')

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
    }
    >>> response = browser.get('/v1/auth/whoami')
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


Logout
======

The user can be logged out::

    >>> response = browser.post('/v1/auth/logout')
    >>> print_json(response)
    {}
