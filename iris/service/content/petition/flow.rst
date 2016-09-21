=============
Petition Flow
=============

Show the full petition creation and lifetime flow.

    >>> import time
    >>> from iris.service.content.petition import Petition


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


Publishing a Petition
=====================

Petition which are draft or rejected can be published::

    >>> petition = {
    ...     "data": {
    ...         "title": "Authenticated"
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)

    >>> id = response.json['data']['id']
    >>> response = browser.post_json('/v1/petitions/%s/event/publish' % id)

After publishing the petition there is one supporter::

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

Reject the petition::

    >>> body = {
    ...     "notify": False
    ... }
    >>> response = browser.post_json('/v1/petitions/%s/event/reject' % id, body)

Publishing again will not add a new supporter::

    >>> response = browser.post_json('/v1/petitions/%s/event/publish' % id)
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


Manage Letter
=============

Letter management start in state "sendLetterRequested" with the creation of a
response token on the petition.

Create a new petition::

    >>> petition = {
    ...     "data": {
    ...         "title": "Manage Letter"
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> id = response.json['data']['id']
    >>> petition = Petition.get(id)
    >>> petition.response_token is None
    True

    >>> _ = browser.post_json('/v1/petitions/%s/event/publish' % id)
    >>> _ = browser.post_json('/v1/petitions/%s/event/approved' % id)
    >>> petition = Petition.get(id)
    >>> petition.supporters = {
    ...     "amount": 11,
    ...     "required": 10,
    ... }
    >>> _ = petition.store(refresh=True)
    >>> _ = browser.post_json('/v1/petitions/%s/event/check' % id)
    >>> petition = Petition.get(id)
    >>> petition.response_token is None
    True
    >>> petition.state.timer = 0
    >>> _ = petition.store(refresh=True)
    >>> _ = browser.post_json('/v1/petitions/%s/event/tick' % id)

Now we are requesting to send a letter::

    >>> petition = Petition.get(id)
    >>> petition.state
    <StateContainer processing.sendLetterRequested>

The token is set::

    >>> token = petition.response_token
    >>> token
    u'...'

Now someone created the letter::

    >>> _ = browser.post_json('/v1/petitions/%s/event/letterSent' % id)

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
    ...         "answer": "machen wir gleich"
    ...     }
    ... }
    >>> response = browser.post_json(
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
    ...         "answer": "machen wir gleich"
    ...     }
    ... }
    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/setFeedback' % id,
    ...     body
    ... )
    >>> print_json(response.json['data']['state'])
    {
      "name": "letterResponseArrived",
      "parent": "processing"
    }
    >>> print_json(response.json['data']['city_answer'])
    "machen wir gleich"

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
