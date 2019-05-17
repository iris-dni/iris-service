=====================
Statemachine Services
=====================


Get Statemachine structure
==========================

Get the petition statemachine::

    >>> response = browser.get('/v1/admin/statemachine/petitions')
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        "states": [
          {
            "name": "draft",
    ...
