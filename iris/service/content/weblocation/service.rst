====================
WebLocation Services
====================


Admin API
=========

The admin API is implemented via the REST mapper.

The browser must be logged in with an administrator::

    >>> _ = ssologin(browser, {'email': 'tester@iris.com', 'roles': ['admin']})


Get WebLocation List
--------------------

Lists all cities::

    >>> response = browser.get('/v1/admin/weblocations')
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": [],
      "total": 0
    }


Create a Web Location
---------------------

Create a new web location::

    >>> wl = {
    ...     "data": {
    ...         "url": "http://www.iris.com",
    ...     }
    ... }
    >>> response = browser.post_json('/v1/admin/weblocations',
    ...                              wl)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        "dc": {
          "created": "...",
          "modified": "..."
        },
        "id": "cd126eaf1870967a2f3d724ee935b379",
        "og": null,
        "state": "visible",
        "url": "http://www.iris.com"
      }
    }

    >>> id = response.json['data']['id']


Update of a Web Location is not allowed
---------------------------------------

Update a WebLocation. It is not possible to update the url::

    >>> wl = {
    ...     "data": {
    ...         "url": "http://www.iris.com/petitions",
    ...         "state": "hidden"
    ...     }
    ... }
    >>> response = browser.post_json('/v1/admin/weblocations/%s' % id,
    ...                              wl)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        "dc": {
          "created": "...",
          "modified": "..."
        },
        "id": "cd126eaf1870967a2f3d724ee935b379",
        "og": null,
        "state": "hidden",
        "url": "http://www.iris.com"
      }
    }



Get a WebLocation by id
-----------------------

Use the id from the response above::

    >>> response = browser.get('/v1/admin/weblocations/%s' % id)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        "dc": {
          "created": "...",
          "modified": "..."
        },
        "id": "cd126eaf1870967a2f3d724ee935b379",
        "og": null,
        "state": "hidden",
        "url": "http://www.iris.com"
      }
    }


Delete a WebLocation
--------------------

Do a delete request::

    >>> response = browser.delete('/v1/admin/weblocations/%s' % id)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        "dc": {
          "created": "...",
          "modified": "..."
        },
        "id": "cd126eaf1870967a2f3d724ee935b379",
        "og": null,
        "state": "hidden",
        "url": "http://www.iris.com"
      }
    }

    >>> response = browser.get('/v1/admin/weblocations/%s' % id,
    ...                        expect_errors=True)
    >>> response.status
    '404 Not Found'
