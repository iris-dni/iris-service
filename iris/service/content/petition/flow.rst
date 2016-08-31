=============
Petition Flow
=============

Show the full petition creation and lifetime flow.


Create Petition
===============

Unauthenticated
---------------

Petitions can be created as unauthenticated user::

    >>> petition = {
    ...     "data": {
    ...         "title": "Unauthenticated"
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> response.status
    '200 OK'

The owner is a session owner::

    >>> print_json(response.json['data']['owner'])
    {
      "class": "User",
      "id": "iris-session:..."
    }

The state is draft::

    >>> print_json(response.json['data']['state'])
    {
      "name": "draft",
      "parent": ""
    }


Authenticated
-------------

With an authenticated session the real user is assigned to the petition::

    >>> _ = ssologin(browser, {'email': 'tester@iris.com'})

    >>> petition = {
    ...     "data": {
    ...         "title": "Authenticated"
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> response.status
    '200 OK'

    >>> print_json(response.json['data']['owner'])
    {
      "class": "User",
      "id": "1Zbfk"
    }
