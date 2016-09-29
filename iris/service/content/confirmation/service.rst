=====================
Confirmation Services
=====================

Prepare test::

    >>> from iris.service.rest.service import testing_push_state
    >>> testing_push_state()

    >>> from iris.service.db.dc import dc_update, dc_now_offset
    >>> from iris.service.content.confirmation.handler import Handler
    >>> from iris.service import rest
    >>> class TestHandler(Handler, rest.RESTMapper):
    ...
    ...     HANDLER_NAME = 'test'
    ...     NAME = 'confirmations.' + HANDLER_NAME


Permission Settings
===================

The public confirmation API needs an API-Key provided in the header::

    >>> from iris.service.security.policy import API_KEY_HEADER_NAME
    >>> API_KEY_HEADER_NAME
    'X-Iris-Api-Key'

    >>> headers = {
    ...     API_KEY_HEADER_NAME: 'local'
    ... }


Create Confirmation
===================

A new confirmation can be created to get a confirmation token. Additional
`user_data` can be provided which will be provided when confirming the created
confirmation::

    >>> body = {
    ...     "data": {
    ...         "type": "test",
    ...         "data": {
    ...             "whatever": "you",
    ...             "like": True,
    ...         }
    ...     }
    ... }
    >>> response = browser.post_json('/v1/confirmations',
    ...                              body,
    ...                              headers=headers)
    >>> print_json(response)
    {
      "data": {
        "data": {
          "like": true,
          "whatever": "you"
        },
        "id": "..."
      }
    }
    >>> token = response.json['data']['id']


Confirm Confirmation
====================

Confirmations are created to confirm them later::

    >>> response = browser.get('/v1/confirmations/%s/confirm' % token,
    ...                        headers=headers)
    >>> print_json(response)
    {
      "data": {
        "data": {
          "like": true,
          "whatever": "you"
        }
      }
    }

Confirm the confirmed confirmation::

    >>> response = browser.get('/v1/confirmations/%s/confirm' % token,
    ...                        headers=headers,
    ...                        expect_errors=True
    ...                       )
    >>> print_json(response)
    {
      "error": {
        "code": 400,
        "description": "Bad request: Already used"
      }
    }


OPTIONS
=======

The options endpoints are callable::

    >>> response = browser.options('/v1/confirmations/%s/confirm' % token)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {}
    >>> print_json({n: v for n,v in response.headers.items() if n.startswith('Access')})
    {
      "Access-Control-Allow-Credentials": "true",
      "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization",
      "Access-Control-Allow-Methods": "POST,GET,DELETE,PUT,OPTIONS",
      "Access-Control-Allow-Origin": "http://localhost",
      "Access-Control-Max-Age": "86400"
    }

    >>> response = browser.options('/v1/confirmations')
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {}
    >>> print_json({n: v for n,v in response.headers.items() if n.startswith('Access')})
    {
      "Access-Control-Allow-Credentials": "true",
      "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization",
      "Access-Control-Allow-Methods": "POST,GET,DELETE,PUT,OPTIONS",
      "Access-Control-Allow-Origin": "http://localhost",
      "Access-Control-Max-Age": "86400"
    }

Test cleanup::

    >>> from iris.service.rest.service import testing_pop_state
    >>> testing_pop_state()
