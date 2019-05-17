========
Security
========


Group Finder
============

The group finder creates a list of groups based on a user::

    >>> request = get_test_request()

    >>> from iris.service.security.security import groupfinder

    >>> groupfinder(None, request)
    []

    >>> user = creators.user()

    >>> groupfinder(user.id, request)
    ['system.Authenticated', 'u:1n3gf']

    >>> user.roles = ['admin']
    >>> _ = user.store()

The roles stored on the user are also added::

    >>> groupfinder(user.id, request)
    ['system.Authenticated', 'u:1n3gf', u'ur:admin']

With an unknown user id::

    >>> groupfinder('unknown', request)
    []


API-Key
=======

There is a special handling for the API-Key user::

    >>> from iris.service.security import acl
    >>> groupfinder(acl.Roles.ApiKeyUser, request)
    ['apikey-user']
