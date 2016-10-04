========================
SMS Confirmation Handler
========================

    >>> request = get_test_request()

Create a petition
=================

The handler `petition_sms` must be used to create an sms confirmation for a
petition.

First a petition is needed::

    >>> petition = creators.petition(
    ...     owner={"mobile": "555 1234"}
    ... )

The data needed to be stored in the confirmation data peroperty must contain
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
=======

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
=============

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
