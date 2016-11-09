====================
Confirmation Handler
====================

Prepare test::

    >>> from iris.service.rest.service import testing_push_state
    >>> testing_push_state()

    >>> import time
    >>> import datetime

A confirmation handler is responsible to create and confirm confirmations. A
handler must be implemented as a RESTMapper which is needed to register the
handler and provide an appropriate interface for the API::

    >>> from iris.service.db.dc import dc_update, iso_now_offset
    >>> from iris.service.content.confirmation.handler import Handler
    >>> from iris.service import rest
    >>> class TestHandler(Handler, rest.RESTMapper):
    ...
    ...     HANDLER_NAME = 'test'
    ...     NAME = 'confirmations.' + HANDLER_NAME
    ...
    ...     NEEDS_CONFIRMATION = True
    ...
    ...     def needs_confirmation(self, data):
    ...         return self.NEEDS_CONFIRMATION
    ...
    ...     def _create(self, confirmation):
    ...         """Send an SMS with the confirmation id
    ...         """
    ...         dc_update(
    ...             confirmation,
    ...             expires=iso_now_offset(datetime.timedelta(seconds=5)),
    ...         )
    ...
    ...     def _confirm(self, confirmation):
    ...         print 'TestHandler confirmed'

The handler can be requested using the RESTMapper::

    >>> request = get_test_request()
    >>> handler = rest.RESTMapper.getMapperImplementation(
    ...     'confirmations.test',
    ...     request,
    ... )
    >>> handler
    <TestHandler object at ...>

Now this hander can be used to create a confirmation::

    >>> data = {
    ...     "data": {
    ...         "data": {
    ...             "any": "data"
    ...         }
    ...     }
    ... }
    >>> result = handler.create(data)
    >>> print_json(result)
    {
      "context_id": null,
      "data": {
        "any": "data"
      },
      "dc": {
        "created": "...",
        "expires": "..."
      },
      "debug": {},
      "handler": "test",
      "id": "...",
      "state": "active"
    }
    >>> id = result['id']

The handler can be used to confirm::

    >>> from iris.service.content.confirmation import Confirmation
    >>> confirmation = Confirmation.get(id)
    >>> result = handler.confirm(confirmation)
    TestHandler confirmed
    >>> print_json(result)
    {
      "context_id": null,
      "data": {
        "any": "data"
      },
      "dc": {
        "created": "...",
        "expires": "..."
      },
      "debug": {},
      "handler": "test",
      "id": "...",
      "state": "used"
    }

Confirm an already confirmed confirmation::

    >>> handler.confirm(confirmation)
    Traceback (most recent call last):
    ValueError: Already used

Confirm an expired confirmation::

    >>> confirmation = Confirmation.get(id)
    >>> _ = dc_update(confirmation, expires=0)
    >>> confirmation.state = 'active'
    >>> _ = confirmation.store(refresh=True)

    >>> handler.confirm(confirmation)
    Traceback (most recent call last):
    ValueError: Expired

Create a confirmation without the service request::

    >>> result = Handler.create_for_handler('test', data, request)
    >>> print_json(result)
    {
      "context_id": null,
      "data": {
        "data": {
          "any": "data"
        }
      },
      "dc": {
        "created": "...",
        "expires": "..."
      },
      "debug": {},
      "handler": "test",
      "id": "...",
      "state": "active"
    }

A handler can prevent the creation of a confirmation::

    >>> TestHandler.NEEDS_CONFIRMATION = False
    >>> Handler.create_for_handler('test', data, request) is None
    True

Test cleanup::

    >>> from iris.service.rest.service import testing_pop_state
    >>> testing_pop_state()
