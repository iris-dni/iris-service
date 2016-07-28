=============
User Document
=============


A user is a `Document`::

    >>> from iris.service.user.document import User
    >>> user = User()
    >>> user
    <User [id=1, '']>

Default dublin core data is set::

    >>> pp(user.dc)
    {
      "created": "...T...+...",
      "modified": "...T...+..."
    }

The state of a user::

    >>> user.state
    'active'

Store the user::

    >>> pp(user.store())
    {
      "_id": "1",
      "_index": "users",
      "_type": "default",
      "_version": 1,
      "created": true
    }

Get the user back from the database::

    >>> user = User.get("1")
    >>> user
    <User [id=1, u'']>
    >>> pp(user.dc)
    {
      "created": "...T...+...",
      "modified": "...T...+..."
    }
    >>> user.state
    u'active'


SSO Data
========

The sso property is an array containing information about different sso
providers::

    >>> user.sso
    []
    >>> user.sso = [
    ...     {'provider': '1', 'trusted': False},
    ...     {'provider': '2', 'trusted': True},
    ... ]
    >>> pp(user.sso)
    [
      {
        "provider": "1",
        "trusted": false
      },
      {
        "provider": "2",
        "trusted": true
      }
    ]

To simplify the update of existing or adding new providers a dict can be
assigned to the property::

    >>> user.sso = {'provider': '1', 'trusted': True}
    >>> pp(user.sso)
    [
      {
        "provider": "1",
        "trusted": true
      },
      {
        "provider": "2",
        "trusted": true
      }
    ]

Add a new provider::

    >>> user.sso = {'provider': '3', 'trusted': False}
    >>> pp(user.sso)
    [
      {
        "provider": "1",
        "trusted": true
      },
      {
        "provider": "2",
        "trusted": true
      },
      {
        "provider": "3",
        "trusted": false
      }
    ]


Roles
=====

User roles are a list of strings::

    >>> user.roles
    []
    >>> user.roles = ['r1']
    >>> user.roles
    ['r1']


Update or Create Users
======================

::

    >>> data = {
    ...     'email': 'email@mail.com',
    ...     'firstname': 'firstname',
    ...     'lastname': 'lastname',
    ...     'roles': ['roles'],
    ...     'sso': {
    ...         'provider': 'apikey',
    ...         'trusted': True,
    ...     },
    ... }
    >>> user = User.update_or_create_by_email(**data)
    >>> user.email
    'email@mail.com'
    >>> user.firstname
    'firstname'
    >>> user.lastname
    'lastname'
    >>> user.roles
    ['roles']
    >>> pp(user.sso)
    [
      {
        "provider": "apikey",
        "trusted": true
      }
    ]

    >>> data = {
    ...     'email': 'email@mail.com',
    ...     'firstname': 'new firstname',
    ...     'lastname': 'new lastname',
    ...     'roles': ['new', 'roles'],
    ...     'sso': {
    ...         'provider': 'apikey',
    ...         'trusted': False,
    ...     },
    ... }
    >>> user = User.update_or_create_by_email(**data)
    >>> user.email
    u'email@mail.com'
    >>> user.firstname
    'new firstname'
    >>> user.lastname
    'new lastname'
    >>> user.roles
    ['new', 'roles']
    >>> pp(user.sso)
    [
      {
        "provider": "apikey",
        "trusted": false
      }
    ]
