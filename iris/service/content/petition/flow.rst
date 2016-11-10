=============
Petition Flow
=============

Show the full petition creation and lifetime flow.

    >>> import time
    >>> from iris.service.db import dc
    >>> from iris.service.content.petition import Petition

A browser which is logged in as an administrator::

    >>> admin = get_browser()
    >>> _ = ssologin(admin, {'email': 'admin@iris.com', 'roles': ['admin']})


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
      "email": "",
      "email_trusted": false,
      "firstname": "",
      "id": "iris-session:...",
      "lastname": "",
      "mobile": "",
      "mobile_trusted": false,
      "street": "",
      "town": "",
      "zip": ""
    }

The state is draft::

    >>> print_json(response.json['data']['state'])
    {
      "letter_wait_expire": null,
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
      "email": "",
      "email_trusted": false,
      "firstname": "",
      "id": "...",
      "lastname": "",
      "mobile": "",
      "mobile_trusted": false,
      "street": "",
      "town": "",
      "zip": ""
    }


Publishing a Petition
=====================

Petitions which are draft or rejected can be published::

    >>> petition = {
    ...     "data": {
    ...         "title": "Authenticated"
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> id = response.json['data']['id']

    >>> publish_body = {"data": {}}
    >>> response = browser.post_json('/v1/petitions/%s/event/publish' % id, publish_body)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        "city": {
          "class": "City",
          "id": null
        },
        ...
        "owner": {
          "class": "User",
          "email": "",
          "email_trusted": false,
          "firstname": "",
          "id": "...",
          "lastname": "",
          "mobile": "",
          "mobile_trusted": false,
          "street": "",
          "town": "",
          "zip": ""
        },
        ...
      },
      "reasons": [
        "mobile_missing",
        "email_missing"
      ],
      "status": "error"
    }

    >>> petition = {
    ...     "data": {
    ...         "owner": {
    ...             "email": "email@iris.com",
    ...             "mobile": "555 1234"
    ...         }
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions/%s' % id, petition)
    >>> response = browser.post_json('/v1/petitions/%s/event/publish' % id, publish_body)
    sendSMS(u'555 1234', 'Petition', u'Your verification code is "..."')
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        ...
        "owner": {
          "class": "User",
          "email": "email@iris.com",
          "email_trusted": false,
          "firstname": "",
          "id": "...",
          "lastname": "",
          "mobile": "555 1234",
          "mobile_trusted": false,
          "street": "",
          "town": "",
          "zip": ""
        },
        ...
      },
      "reasons": [
        "mobile_untrusted"
      ],
      "status": "error"
    }

A confirmation for the mobile number verification was created::

    >>> from iris.service.content.confirmation import Confirmation
    >>> confirmation = Confirmation.search({"query": {"match_all": {}}})['hits']['hits'][0]
    >>> confirmation.data['petition'] == id
    True
    >>> token = confirmation.id

Now we can publish with the confirmation token in the body (this time there is
an email confirmation sent)::

    >>> publish_confirm_body = {
    ...     "data": {
    ...         "mobile_token": token
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions/%s/event/publish' % id, publish_confirm_body)
    {'message': {'global_merge_vars': [{'content': {'url': u'http://frontend/confirm/petition/email?key=...'},
    ...
                 'to': [{'email': u'email@iris.com', 'type': 'to'}]},
     'template_content': [],
     'template_name': 'iris-petition-mailconfirmation'}
    >>> print_json(response)
    {
      "data": {
        ...
      },
      "status": "ok"
    }

There is already a supporter::

    >>> print_json(response.json['data']['supporters'])
    {
      "amount": 1,
      "required": ...
    }

Reject the petition::

    >>> body = {
    ...     "notify": False
    ... }
    >>> response = admin.post_json('/v1/petitions/%s/event/reject' % id, body)

Publishing again will not add a new supporter::

    >>> response = browser.post_json('/v1/petitions/%s/event/publish' % id, publish_body)
    >>> print_json(response)
    {
      "data": {
        ...
        "supporters": {
          "amount": 1,
          "required": ...
        },
        ...
      },
      "status": "ok"
    }

SMS send errors provide a bad request response::

    >>> body = {
    ...     "notify": False
    ... }
    >>> response = admin.post_json('/v1/petitions/%s/event/reject' % id, body)
    >>> petition = {
    ...     "data": {
    ...         "owner": {
    ...             "mobile": "555 333"
    ...         }
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions/%s' % id, petition)
    >>> response = browser.post_json('/v1/petitions/%s/event/publish' % id, publish_body, expect_errors=True)
    >>> print_json(response)
    {
      "error": {
        "code": 400,
        "description": "Bad request: Can't send SMS"
      }
    }

Providing a wrong confirmation code::

    >>> petition = {
    ...     "data": {
    ...         "owner": {
    ...             "mobile": "555 444"
    ...         }
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions/%s' % id, petition)
    >>> publish_body = {
    ...     "data": {
    ...         "mobile_token": "unknown"
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions/%s/event/publish' % id, publish_body)
    >>> print_json(response)
    {
      "data": {
        ...
      },
      "reasons": [
        "mobile_verification_failed"
      ],
      "status": "error"
    }


Manage Letter
=============

Letter management start in state "sendLetterRequested" with the creation of a
response token on the petition.

Create a new petition::

    >>> city = creators.city(id='4242',
    ...                      provider='petition_events',
    ...                      name='HongKong',
    ...                      treshold=42,
    ...                      location={'url':'https://www.hongkong.com'},
    ...                     )
    >>> petition = {
    ...     "data": {
    ...         "title": "Manage Letter",
    ...         "city": {"id": city.id},
    ...         "owner": {
    ...             "email": "email@iris.com",
    ...             "mobile": "555 1234"
    ...         }
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> id = response.json['data']['id']
    >>> petition = Petition.get(id)
    >>> petition.response_token is None
    True
    >>> petition.owner = {"mobile_trusted": True, "email_trusted": True}
    >>> _ = petition.store(refresh=True)

    >>> _ = browser.post_json('/v1/petitions/%s/event/publish' % id, publish_body)
    >>> _ = admin.post_json('/v1/petitions/%s/event/approved' % id)
    >>> petition = Petition.get(id)
    >>> petition.state.tick
    True

Make the petition a winner::

    >>> petition = Petition.get(id)
    >>> petition.supporters = {
    ...     "amount": 11,
    ...     "required": 10,
    ... }
    >>> _ = petition.store(refresh=True)
    >>> _ = admin.post_json('/v1/petitions/%s/event/check' % id)
    >>> petition = Petition.get(id)
    >>> petition.state
    <StateContainer supportable.winner>
    >>> petition.response_token is None
    True
    >>> petition.state.tick
    True

Let the support time expire::

    >>> _ = dc.dc_update(petition, **{dc.DC_EXPIRES: dc.time_now()})
    >>> _ = petition.store(refresh=True)
    >>> _ = admin.post_json('/v1/petitions/%s/event/tick' % id)

Now we are requesting to send a letter::

    >>> petition = Petition.get(id)
    >>> petition.state
    <StateContainer processing.sendLetterRequested>
    >>> petition.state.tick
    False

The token is set::

    >>> token = petition.response_token
    >>> token
    u'...'

Now someone created the letter::

    >>> response = admin.post_json('/v1/petitions/%s/event/letterSent' % id)
    >>> print_json(response.json['data']['state'])
    {
      "letter_wait_expire": "...",
      "name": "waitForLetterResponse",
      "parent": "processing"
    }

    >>> petition = Petition.get(id)
    >>> petition.state
    <StateContainer processing.waitForLetterResponse>

The token is still the same::

    >>> petition.response_token == token
    True

The token can be used to get the corresponding petition::

    >>> response = browser.get('/v1/token/%s/petitions' % token)
    >>> response.json['data']['id'] == id
    True

Now the feedback can be set if the token is correct::

    >>> body = {
    ...     "data": {
    ...         "token": "wrong token",
    ...         "answer": {
    ...             "text": "machen wir gleich",
    ...             "name": "I wrote it"
    ...         }
    ...     }
    ... }
    >>> response = admin.post_json(
    ...     '/v1/petitions/%s/event/setFeedback' % id,
    ...     body,
    ...     expect_errors=True
    ... )
    >>> print_json(response)
    {
      "error": {
        "code": 400,
        "description": "Wrong token provided"
      }
    }

With a valid token the feedback can be set::

    >>> body = {
    ...     "data": {
    ...         "token": token,
    ...         "answer": {
    ...             "text": "machen wir gleich",
    ...             "name": "I wrote it"
    ...         }
    ...     }
    ... }
    >>> response = admin.post_json(
    ...     '/v1/petitions/%s/event/setFeedback' % id,
    ...     body
    ... )
    >>> print_json(response.json['data']['state'])
    {
      "letter_wait_expire": "...",
      "name": "letterResponseArrived",
      "parent": "processing"
    }
    >>> print_json(response.json['data']['city_answer'])
    {
      "name": "I wrote it",
      "text": "machen wir gleich"
    }

The petition is no longer available via the token::

    >>> response = browser.get(
    ...     '/v1/token/%s/petitions' % token,
    ...     expect_errors=True,
    ... )
    >>> print_json(response)
    {
      "error": {
        "code": 404,
        "description": "Token '...' for content type 'petitions' not found"
      }
    }
