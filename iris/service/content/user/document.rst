=============
User Document
=============


A user is a `Document`::

    >>> from iris.service.content.user.document import User
    >>> user = User()
    >>> user
    <User [id=u'1n3gf', '']>

Default dublin core data is set::

    >>> pp(user.dc)
    {
      "created": "...T...+...",
      "modified": "...T...+..."
    }

The state of a user::

    >>> user.state
    'active'

    >>> user.email = "me@home.com"
    >>> user.email_trusted = True
    >>> user.mobile = "555 123"
    >>> user.mobile_trusted = False

Store the user::

    >>> pp(user.store())
    {
      "_id": "1n3gf",
      "_index": "users",
      "_type": "default",
      "_version": 1,
      "created": true
    }

Get the user back from the database::

    >>> user = User.get("1n3gf")
    >>> user
    <User [id=u'1n3gf', u'me@home.com']>
    >>> pp(user.dc)
    {
      "created": "...T...+...",
      "modified": "...T...+..."
    }
    >>> user.state
    u'active'
    >>> user.email
    u'me@home.com'
    >>> user.email_trusted
    True
    >>> user.mobile
    u'555 123'
    >>> user.mobile_trusted
    False


SSO Data
========

The sso property is an array containing information about different sso
providers::

    >>> user.sso
    []
    >>> user.sso = [
    ...     {'provider': '1', "more": "data"},
    ...     {'provider': '2'},
    ... ]
    >>> pp(user.sso)
    [
      {
        "more": "data",
        "provider": "1"
      },
      {
        "provider": "2"
      }
    ]

To simplify the update of existing or adding new providers a dict can be
assigned to the property::

    >>> user.sso = {'provider': '1', 'even': 'more data'}
    >>> pp(user.sso)
    [
      {
        "even": "more data",
        "more": "data",
        "provider": "1"
      },
      {
        "provider": "2"
      }
    ]

Add a new provider::

    >>> user.sso = {'provider': '3'}
    >>> pp(user.sso)
    [
      {
        "even": "more data",
        "more": "data",
        "provider": "1"
      },
      {
        "provider": "2"
      },
      {
        "provider": "3"
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


Trusted flag updates
====================

email_trusted
-------------

An update can set the flag but not reset::

    >>> data = {
    ...     'email': 'u1@mail.com',
    ...     'email_trusted': False
    ... }
    >>> user = User.update_or_create_by_email(**data)
    >>> user.email_trusted
    False

    >>> data = {
    ...     'email': 'u1@mail.com',
    ...     'email_trusted': True
    ... }
    >>> user = User.update_or_create_by_email(**data)
    >>> user.email_trusted
    True

    >>> data = {
    ...     'email': 'u1@mail.com',
    ...     'email_trusted': False
    ... }
    >>> user = User.update_or_create_by_email(**data)
    >>> user.email_trusted
    True


mobile_trusted
--------------

An update can set the flag but not reset::

    >>> data = {
    ...     'email': 'u1@mail.com',
    ...     'mobile': '555 1234',
    ...     'mobile_trusted': False
    ... }
    >>> user = User.update_or_create_by_email(**data)
    >>> user.mobile_trusted
    False

    >>> data = {
    ...     'email': 'u1@mail.com',
    ...     'mobile_trusted': True
    ... }
    >>> user = User.update_or_create_by_email(**data)
    >>> user.mobile_trusted
    True

    >>> data = {
    ...     'email': 'u1@mail.com',
    ...     'mobile_trusted': False
    ... }
    >>> user = User.update_or_create_by_email(**data)
    >>> user.mobile_trusted
    True

An update can reset the flag if the mobile number is changed::

    >>> data = {
    ...     'email': 'u1@mail.com',
    ...     'mobile': '555 1234',
    ...     'mobile_trusted': False
    ... }
    >>> user = User.update_or_create_by_email(**data)
    >>> user.mobile_trusted
    True

    >>> data = {
    ...     'email': 'u1@mail.com',
    ...     'mobile': '555 4242',
    ...     'mobile_trusted': False
    ... }
    >>> user = User.update_or_create_by_email(**data)
    >>> user.mobile_trusted
    False
