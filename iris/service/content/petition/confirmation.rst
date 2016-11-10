========================
SMS Confirmation Handler
========================

    >>> request = get_test_request()


Petition Mobile Confirmation
============================


Create Confirmation
-------------------

The handler `petition_sms` must be used to create an sms confirmation for a
petition.

First a petition is needed::

    >>> petition = creators.petition(
    ...     owner={"mobile": "555 1234"}
    ... )

The data needed to be stored in the confirmation data property must contain
the petition id::

    >>> data = {
    ...     "data": {
    ...         "petition": petition.id
    ...     }
    ... }

Create the confirmation::

    >>> from iris.service.content.confirmation.handler import Handler
    >>> response = Handler.create_for_handler('petition_sms', data, request)
    sendSMS(u'555 1234', 'Petition', u'Your verification code is "..."')
    >>> print_json(response)
    {
      "context_id": null,
      "data": {
        "mobile": "555 1234",
        "petition": "..."
      },
      "dc": {
        "created": "...",
        "expires": "..."
      },
      "debug": {
        "sms": {
          "phone_number": "555 1234",
          "response": {},
          "subject": "Petition",
          "text": "Your verification code is \"...\""
        }
      },
      "handler": "petition_sms",
      "id": "...",
      "state": "active"
    }
    >>> response["data"]["petition"] == petition.id
    True

    >>> token = response["id"]


Confirm
-------

The confirmation API can be used with the id of the confirmation object::

    >>> from iris.service.security.policy import API_KEY_HEADER_NAME
    >>> headers = {
    ...     API_KEY_HEADER_NAME: 'local'
    ... }
    >>> response = browser.get('/v1/confirmations/%s/confirm' % token,
    ...                        headers=headers)
    >>> print_json(response)
    {
      "data": {
        "data": {
          "mobile": "555 1234",
          "petition": "1n3gf"
        }
      }
    }

Now the trusted flag in the petition is set to true::

    >>> petition = petition.get(petition.id)
    >>> print_json(petition.owner.relation_dict)
    {
      ...
      "mobile": "555 1234",
      "mobile_trusted": true,
      ...
    }

Multiple confirmations are not allowed::

    >>> response = browser.get('/v1/confirmations/%s/confirm' % token,
    ...                        headers=headers,
    ...                        expect_errors=True)
    >>> print_json(response)
    {
      "error": {
        "code": 400,
        "description": "Bad request: Already used"
      }
    }


Special Cases
-------------

The mobile number must be provided in the owner relation of the petition::

    >>> petition = creators.petition()
    >>> data = {
    ...     "data": {
    ...         "petition": petition.id
    ...     }
    ... }
    >>> response = Handler.create_for_handler('petition_sms', data)
    Traceback (most recent call last):
    ValueError: Missing mobile number


Petition Email Confirmation
===========================


Create Confirmation
-------------------

The handler `petition_confirm_email` must be used to create an email
confirmation for a petition.

First a petition is needed::

    >>> city = creators.city(
    ...     id="100042",
    ...     provider="test",
    ...     location={"url": "https://www.aargauerzeitung.ch"},
    ...     name="aarau",
    ... )
    >>> petition = creators.petition(
    ...     owner={
    ...         "email": "humpty@bumpty.ch",
    ...         "firstname": "Humpty",
    ...         "lastname": "Bumpty",
    ...     },
    ...     city=city
    ... )

The data needed to be stored in the confirmation data property must contain
the petition id::

    >>> data = {
    ...     "data": {
    ...         "template": 'iris-emailconfirmation',
    ...         "petition": petition.id
    ...     }
    ... }

Create the confirmation::

    >>> from iris.service.content.confirmation.handler import Handler
    >>> response = Handler.create_for_handler('petition_confirm_email', data, request)
    {'message': {'global_merge_vars': [{'content': {'url': u'http://frontend/confirm/petition/email?key=...'},
                                        'name': 'confirm'},
                                       {'content': {'city': {u'contact': {},
                                                             'id': u'test:100042',
                                                             u'name': u'aarau',
                                                             u'portal': {},
                                                             u'provider': u'test',
                                                             u'state': u'active',
                                                             u'tags': [],
                                                             u'treshold': -1,
                                                             u'zips': []},
                                                    u'city_answer': {u'name': u'',
                                                                     u'text': u''},
                                                    u'dc': {u'created': u'...',
                                                            u'effective': None,
                                                            u'expires': None,
                                                            u'modified': u'...'},
                                                    u'description': u'',
                                                    u'id': u'...',
                                                    'images': [],
                                                    'links': [],
                                                    'mentions': [],
                                                    'owner': {u'email': u'humpty@bumpty.ch',
                                                              u'email_trusted': False,
                                                              u'firstname': u'Humpty',
                                                              u'lastname': u'Bumpty',
                                                              u'mobile': u'',
                                                              u'mobile_trusted': False,
                                                              u'street': u'',
                                                              u'town': u'',
                                                              u'zip': u''},
                                                    u'state': {u'letter_wait_expire': None,
                                                               u'listable': False,
                                                               u'name': u'draft',
                                                               u'parent': u'',
                                                               u'tick': False},
                                                    u'suggested_solution': u'',
                                                    u'supporters': {u'amount': 0,
                                                                    'remaining': 0,
                                                                    u'required': 0},
                                                    u'tags': [],
                                                    u'title': u'',
                                                    u'type': u''},
                                        'name': 'petition'}],
                 'merge_vars': [{'rcpt': u'humpty@bumpty.ch',
                                 'vars': [{'content': {'class': 'User',
                                                       u'email': u'humpty@bumpty.ch',
                                                       u'email_trusted': False,
                                                       u'firstname': u'Humpty',
                                                       u'id': None,
                                                       u'lastname': u'Bumpty',
                                                       u'mobile': u'',
                                                       u'mobile_trusted': False,
                                                       u'street': u'',
                                                       u'town': u'',
                                                       u'zip': u''},
                                           'name': 'user'}]}],
                 'to': [{'email': u'humpty@bumpty.ch',
                         'name': u'Humpty Bumpty',
                         'type': 'to'}]},
     'template_content': [],
     'template_name': 'iris-petition-mailconfirmation'}

    >>> print_json(response)
    {
      "context_id": "iris-petition-mailconfirmation...",
      "data": {
        "email": "humpty@bumpty.ch",
        "petition": "...",
        "template": "iris-emailconfirmation"
      },
      "dc": {
        "created": "...",
        "expires": "..."
      },
      "debug": {
        "mail": {}
      },
      "handler": "petition_confirm_email",
      "id": "...",
      "state": "active"
    }
    >>> response["data"]["petition"] == petition.id
    True

    >>> token = response["id"]

No confirmation is created as long there is an open confirmation::

    >>> Handler.create_for_handler('petition_confirm_email', data, request) is None
    True


Confirm Mobile
--------------

Before the confirmation we have an untrusted email::

    >>> petition = petition.get(petition.id)
    >>> print_json(petition.owner.relation_dict)
    {
      ...
      "email": "humpty@bumpty.ch",
      "email_trusted": false,
      ...
    }

The confirmation API can be used with the id of the confirmation object::

    >>> from iris.service.security.policy import API_KEY_HEADER_NAME
    >>> headers = {
    ...     API_KEY_HEADER_NAME: 'local'
    ... }
    >>> response = browser.get('/v1/confirmations/%s/confirm' % token,
    ...                        headers=headers)
    >>> print_json(response)
    {
      "data": {
        "data": {
          "email": "humpty@bumpty.ch",
          "petition": "1fjnH",
          "template": "iris-emailconfirmation"
        }
      }
    }

Now the trusted flag in the petition is set to true::

    >>> petition = petition.get(petition.id)
    >>> print_json(petition.owner.relation_dict)
    {
      ...
      "email": "humpty@bumpty.ch",
      "email_trusted": true,
      ...
    }

Multiple confirmations are not allowed::

    >>> response = browser.get('/v1/confirmations/%s/confirm' % token,
    ...                        headers=headers,
    ...                        expect_errors=True)
    >>> print_json(response)
    {
      "error": {
        "code": 400,
        "description": "Bad request: Already used"
      }
    }


Special Cases for Mobile
------------------------

The mobile number must be provided in the owner relation of the petition::

    >>> petition = creators.petition()
    >>> data = {
    ...     "data": {
    ...         "petition": petition.id
    ...     }
    ... }
    >>> response = Handler.create_for_handler('petition_sms', data)
    Traceback (most recent call last):
    ValueError: Missing mobile number



Support Confirmation
====================


Create a Mobile Confirmation
----------------------------

The handler `support_sms` must be used to create an sms confirmation for a
petition support.

The data needed to be stored in the confirmation data property must contain
the mobile number::

    >>> data = {
    ...     "data": {
    ...         "user_id": None,
    ...         "user": {
    ...             "mobile": "555 1234"
    ...         },
    ...         "petition": petition.id
    ...     }
    ... }

Create the confirmation::

    >>> response = Handler.create_for_handler('support_sms', data, request)
    sendSMS('555 1234', 'Support', u'Your verification code is "..."')
    >>> print_json(response)
    {
      "context_id": null,
      "data": {
        "petition": "...",
        "user": {
          "mobile": "555 1234"
        },
        "user_id": null
      },
      "dc": {
        "created": "...",
        "expires": "..."
      },
      "debug": {
        "sms": {
          "phone_number": "555 1234",
          "response": {},
          "subject": "Support",
          "text": "Your verification code is \"...\""
        }
      },
      "handler": "support_sms",
      "id": "...",
      "state": "active"
    }

    >>> token = response["id"]


Confirm
-------

Directly use the handler to confirm::

    >>> response = Handler.confirm_handler('support_sms', token, request)
    >>> print_json(response)
    {
      "context_id": null,
      "data": {
        "petition": "...",
        "user": {
          "mobile": "555 1234"
        },
        "user_id": null
      },
      "dc": {
        "created": "...",
        "expires": "..."
      },
      "debug": {
        "sms": {
          "phone_number": "555 1234",
          "response": {},
          "subject": "Support",
          "text": "Your verification code is \"...\""
        }
      },
      "handler": "support_sms",
      "id": "...",
      "state": "used"
    }

Multiple uses are not allowed::

    >>> response = Handler.confirm_handler('support_sms', token, request)
    Traceback (most recent call last):
    ValueError: Already used
