====================
Authentication Views
====================


Login Embed Code
================

This is the endpoint from which an sso enabled foreign page must load the IRSI
javascript for the login page::

    >>> response = browser.get('/v1/views/iris-sso-login.js')
    >>> response.status
    '200 OK'
    >>> print response.body
    (function iris_sso_login(global) {
    ...
    })(window);
