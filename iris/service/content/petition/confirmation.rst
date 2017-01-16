========================
SMS Confirmation Handler
========================

    >>> request = get_test_request()


Petition Mobile Confirmation
============================


Create a Mobile Confirmation
----------------------------

The handler `petition_sms` must be used to create an sms confirmation for a
petition.

First a petition is needed::

    >>> owner = creators.user(
    ...     email="petition-owner@iris.com",
    ...     email_trusted=False,
    ...     mobile="555 424242",
    ...     mobile_trusted=False,
    ... )
    >>> petition = creators.petition(
    ...     owner={
    ...         "id": owner.id,
    ...         "mobile": "555 1234",
    ...     }
    ... )

The data needed to be stored in the confirmation data property must contain
the petition id::

    >>> data = {
    ...     "data": {
    ...         "petition": petition.id
    ...     },
    ...     "info": {
    ...         "petition": petition.id
    ...     }
    ... }

Create the confirmation::

    >>> from iris.service.content.confirmation.handler import Handler
    >>> response = Handler.create_for_handler('petition_sms', data, request)
    sendSMS(u'+415551234', u'...')
    >>> print_json(response)
    {
      "context_id": "...-...",
      "data": {
        "mobile": "+415551234",
        "petition": "...",
        "token": "..."
      },
      "dc": {
        "created": "...",
        "expires": "..."
      },
      "debug": {
        "sms": {
          "phone_number": "+415551234",
          "response": {},
          "text": "Dein Code für petitio.ch ist\n ..."
        }
      },
      "handler": "petition_sms",
      "id": "...",
      "response": {
        "petition": "..."
      },
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
        "petition": "..."
      }
    }

Now the trusted flag of the owner relation in the petition is set to true::

    >>> petition = petition.get(petition.id)
    >>> print_json(petition.owner.relation_dict)
    {
      ...
      "mobile": "+415551234",
      "mobile_trusted": true,
      ...
    }

Also the user mobile_trusted and phone is set::

    >>> from iris.service.content.user import User
    >>> User.get(owner.id).mobile
    u'+415551234'
    >>> User.get(owner.id).mobile_trusted
    True

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

    >>> owner = creators.user(
    ...     email="humpty@bumpty.ch",
    ...     email_trusted=False,
    ...     mobile="555 1234",
    ...     mobile_trusted=False,
    ... )
    >>> city = creators.city(
    ...     id="100042",
    ...     provider="test",
    ...     location={"url": "https://www.aargauerzeitung.ch"},
    ...     name="aarau",
    ... )
    >>> petition = creators.petition(
    ...     owner={
    ...         "id": owner.id,
    ...         "email": "humpty@bumpty.ch",
    ...         "firstname": "Humpty",
    ...         "lastname": "Bumpty",
    ...         "salutation": "salutation",
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

    >>> from iris.service import mail
    >>> print_json(mail.TESTING_MAIL_STACK[-1])
    {
      "message": {
        "global_merge_vars": [
          {
            "content": {
              "url": "http://frontend/confirm/email/petition?key=..."
            },
            "name": "confirm"
          },
    ...
            "name": "petition"
          },
          {
            "content": {
              "url": "http://frontend"
            },
            "name": "portal"
          }
        ],
        "merge_vars": [
          {
            "rcpt": "humpty@bumpty.ch",
            "vars": [
    ...
                "name": "user"
              }
            ]
          }
        ],
        "to": [
          {
            "email": "humpty@bumpty.ch",
            "name": "Humpty Bumpty",
            "type": "to"
          }
        ]
      },
      "template_content": [],
      "template_name": "iris-petition-mailconfirmation"
    }

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
      "response": {
        "petition": "..."
      },
      "state": "active"
    }
    >>> response["data"]["petition"] == petition.id
    True

    >>> token = response["id"]

No confirmation is created as long there is an open confirmation::

    >>> Handler.create_for_handler('petition_confirm_email', data, request) is None
    True


Confirm
-------

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
        "petition": "..."
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

The user email_trusted and salutation is set::

    >>> from iris.service.content.user import User
    >>> u = User.get(owner.id)
    >>> u.email_trusted
    True
    >>> u.salutation
    u'salutation'

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


Support Mobile Confirmation
===========================


Create Confirmation
-------------------

The handler `support_sms` must be used to create an sms confirmation for a
petition support.

The data needed to be stored in the confirmation data property must contain
the mobile number::

    >>> data = {
    ...     "data": {
    ...         "user_id": None,
    ...         "user": {
    ...             "mobile": "555 1234",
    ...             "salutation": "mobile",
    ...         },
    ...         "petition": petition.id
    ...     }
    ... }

Create the confirmation::

    >>> response = Handler.create_for_handler('support_sms', data, request)
    sendSMS('555 1234', u'...')
    >>> print_json(response)
    {
      "context_id": "...-...",
      "data": {
        "petition": "...",
        "token": "...",
        "user": {
          "mobile": "555 1234",
          "salutation": "mobile"
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
          "text": "..."
        }
      },
      "handler": "support_sms",
      "id": "...",
      "response": {
        "petition": "..."
      },
      "state": "active"
    }

    >>> token = response["id"]


Confirm
-------

Directly use the handler to confirm::

    >>> response = Handler.confirm_handler('support_sms', token, request)
    >>> print_json(response)
    {
      "petition": "..."
    }

Multiple uses are not allowed::

    >>> response = Handler.confirm_handler('support_sms', token, request)
    Traceback (most recent call last):
    ValueError: Already used


Support Email Confirmation
==========================

    >>> user = creators.user(email="supporter@home.com")
    >>> supporter = petition.addSupporter(request, user.id, {'email': 'holla@123.com'})
    >>> _ = supporter.store(refresh=True)
    >>> data = {
    ...     "data": {
    ...         "petition": petition.id,
    ...         "supporter": supporter.id,
    ...     }
    ... }
    >>> response = Handler.create_for_handler(
    ...     'supporter_confirm_email',
    ...     data,
    ...     request)
    >>> print_json(response)
    {
      "context_id": null,
      "data": {
        "email": "holla@123.com",
        "petition": "...",
        "supporter": "...-u:..."
      },
      "dc": {
        "created": "...",
        "expires": "..."
      },
      "debug": {
        "mail": {}
      },
      "handler": "supporter_confirm_email",
      "id": "...",
      "response": {
        "petition": "..."
      },
      "state": "active"
    }

    >>> from iris.service import mail
    >>> print_json(mail.TESTING_MAIL_STACK[-1])
    {
      "message": {
        "global_merge_vars": [
          {
            "content": {
              "url": "http://frontend/confirm/email/supporter?key=..."
            },
            "name": "confirm"
          },
    ...
            "name": "petition"
          },
          {
            "content": {
              "url": "http://frontend"
            },
            "name": "portal"
          }
        ],
        "merge_vars": [
          {
            "rcpt": "holla@123.com",
            "vars": [
    ...
                "name": "user"
              }
            ]
          }
        ],
        "to": [
          {
            "email": "holla@123.com",
            "type": "to"
          }
        ]
      },
      "template_content": [],
      "template_name": "iris-supporter-mailconfirmation"
    }
