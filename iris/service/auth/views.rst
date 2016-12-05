====================
Authentication Views
====================


Login Embed Code
================

This is the endpoint from which an sso enabled foreign page must load the IRIS
javascript for the login page::

    >>> response = browser.get('/v1/views/iris-sso-login.js')
    >>> response.headers['content-type']
    'application/javascript; charset=UTF-8'
    >>> response.status
    '200 OK'
    >>> print response.body
    (function iris_sso_login(global) {
    ...
            ssoapicall('http://testing.com/v1/auth/whoami', 'get', callback);
    ...
            ssoapicall('http://testing.com/v1/auth/ssotoken', 'post', callback);
    ...
                        var redirectUrl = 'http://testing.com/v1/views/iris-sso-redirect.html?token=' + token + '&redirecturl=' + retUrl;
    ...
    })(window);


SSO Login Redirect
==================

We need a valid token to use the redirect endpoint::

    >>> from iris.service.auth.sso import sign_message
    >>> message = sign_message(
    ...     {
    ...         'email': 'me-sso@you.com',
    ...         'firstname': 'hoschi',
    ...         'roles': ['admin'],
    ...     },
    ...     'test_public_api_key',
    ... )
    >>> response = browser.post('/v1/auth/ssotoken'
    ...                         '?sso=%s'
    ...                         '&apikey=test_public_api_key' % message)
    >>> token = response.json['token']

Now the redirect endpoint sets the authentication cookie and redirects::

    >>> response = browser.get('/v1/views/iris-sso-redirect.html?token=%s&redirecturl=/' % token)
    >>> response.status
    '302 Found'
    >>> response.headers['location']
    'http://localhost/'
    >>> response.headers['set-cookie']
    'iris-tkt="...!userid_type:b64unicode"; Domain=.localhost; Path=/'

With an invalid token we are redirected::

    >>> response = browser.get('/v1/views/iris-sso-redirect.html?token=123&redirecturl=/')
    >>> response.status
    '302 Found'
    >>> response.headers['location']
    'http://localhost/'
    >>> response.headers['set-cookie']
    'iris-tkt=; Domain=.localhost; Max-Age=0; Path=/; expires=Wed, 31-Dec-97 23:59:59 GMT'

    >>> response = browser.get('/v1/views/iris-sso-redirect.html?redirecturl=/')
    >>> response.status
    '302 Found'
    >>> response.headers['location']
    'http://localhost/'
    >>> response.headers['set-cookie']
    'iris-tkt=; Domain=.localhost; Max-Age=0; Path=/; expires=Wed, 31-Dec-97 23:59:59 GMT'
