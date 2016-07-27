========
Security
========


Group Finder
============

The group finder creates a list of groups based on a user::

    >>> request = get_test_request()

    >>> from iris.service.auth.security import groupfinder

    >>> groupfinder(None, request)
    []

    >>> user = creators.user()

    >>> groupfinder(user.id, request)
    ['system.Authenticated', 'u:1']

    >>> user.roles = ['admin']
    >>> _ = user.store()

The roles stored on the user are also added::

    >>> groupfinder(user.id, request)
    ['system.Authenticated', 'u:1', u'ur:admin']

With an unknown user id::

    >>> groupfinder('unknown', request)
    []
