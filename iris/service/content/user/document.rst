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
    u'+41555123'
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
    ...     'salutation': 'salutation',
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
    >>> user.salutation
    'salutation'
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


Obfuscate Phone Number
----------------------

A utility function helps to obfuscate phone numbers for public use::

    >>> from iris.service.content.user.document import obfuscate_phone_number

    >>> obfuscate_phone_number('+41794578256')
    '+41 79 XXX XX 56'

    >>> obfuscate_phone_number('0041794578256')
    '+41 79 XXX XX 56'

Edge cases::

    >>> obfuscate_phone_number('+4179')
    'XXX XX'

    >>> obfuscate_phone_number('+41794')
    'XXX XX'

    >>> obfuscate_phone_number('+417945')
    '+41 79 XXX XX 45'

    >>> obfuscate_phone_number('00417')
    'XXX XX'

    >>> obfuscate_phone_number('004179')
    'XXX XX'

    >>> obfuscate_phone_number('0041794')
    'XXX XX'

    >>> obfuscate_phone_number('00417945')
    '+41 79 XXX XX 45'


Normalise Phone Number
----------------------

Phone numbers are normalised::

    >>> from iris.service.content.user.document import normalise_phone_number
    >>> normalise_phone_number('0041 123456789')
    u'+41123456789'

    >>> normalise_phone_number('0041123456789')
    u'+41123456789'

    >>> normalise_phone_number('0041 1 2 345 67     89')
    u'+41123456789'

    >>> normalise_phone_number('+41 123456789')
    u'+41123456789'

    >>> normalise_phone_number('+41 123 4 5     67 89')
    u'+41123456789'

A number without a country code is transformed to a 'swiss number'::

    >>> normalise_phone_number('123 4 5  67 89')
    u'+41123456789'

Different (explicit) country codes than swiss remain::

    >>> normalise_phone_number('+43 123 4567 89')
    u'+43123456789'

    >>> normalise_phone_number('+49 123 4567 89')
    u'+49123456789'

Edge case numbers which cause 'phonenumbers' package to throw an exception and
our own, primitive version takes over::

    >>> normalise_phone_number(u'+08(2)9338238082')
    u'+0829338238082'

    >>> normalise_phone_number(u'+08 (2)9   3 3 82   380 82')
    u'+0829338238082'

    >>> normalise_phone_number(u'008 (2)9   3 3 82   380 82')
    u'+829338238082'

    >>> normalise_phone_number(u'+08 (2) 9   3 3 82   380 82')
    u'+0829338238082'
