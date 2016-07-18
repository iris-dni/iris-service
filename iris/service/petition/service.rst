=================
Petition Services
=================


Public API
==========

The public API contains the endpoints which are available for the frontend.


Create Petition
---------------

    >>> petition = {
    ...     "data": {
    ...         "state": "test"
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        ...
        "dc": {
          "created": "...",
          "effective": null,
          "expires": null,
          "modified": "..."
        },
        ...
        "id": ...,
        ...
        "state": "draft",
        ...
      }
    }

    >>> id = response.json['data']['id']


Get Petition
------------

    >>> response = browser.get('/v1/petitions/%s' % id)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        ...
        "dc": {
          "created": "...",
          "effective": null,
          "expires": null,
          "modified": "..."
        },
        ...
        "id": ...,
        ...
        "state": "draft",
        ...
      }
    }


Delete Petition
---------------

    >>> response = browser.delete('/v1/petitions/%s' % id)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        ...
        "dc": {
          "created": "...",
          "effective": null,
          "expires": null,
          "modified": "..."
        },
        ...
        "id": ...,
        ...
        "state": "draft",
        ...
      }
    }

    >>> response = browser.get('/v1/petitions/%s' % id, expect_errors=True)
    >>> response.status
    '404 Not Found'


Admin API
=========

The admin API is implemented via the REST mapper.

Get Petition List
-----------------

    >>> response = browser.get('/v1/admin/petitions')
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": [],
      "total": 0
    }


Create a Petition
-----------------

Create a new petition::

    >>> petition = {
    ...     "data": {
    ...         "state": "test 1"
    ...     }
    ... }
    >>> response = browser.post_json('/v1/admin/petitions',
    ...                              petition)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        ...
        "dc": {
          "created": "...",
          "effective": null,
          "expires": null,
          "modified": "..."
        },
        ...
        "id": ...,
        ...
        "state": "test 1",
        ...
      }
    }

    >>> id = response.json['data']['id']


Update a Petition
-----------------

POST on the petition with the data which need to be changed::

    >>> petition = {
    ...     "data": {
    ...         "state": "changed 1"
    ...     }
    ... }
    >>> response = browser.post_json('/v1/admin/petitions/%s' % id,
    ...                              petition)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        ...
        "dc": {
          "created": "...",
          "effective": null,
          "expires": null,
          "modified": "..."
        },
        ...
        "id": ...,
        ...
        "state": "changed 1",
        ...
      }
    }


Get a Petition by id
--------------------

Use the id from the response above::

    >>> response = browser.get('/v1/admin/petitions/%s' % id)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        ...
        "dc": {
          "created": "...",
          "effective": null,
          "expires": null,
          "modified": "..."
        },
        ...
        "id": ...,
        ...
        "state": "changed 1",
        ...
      }
    }


List Petitions
--------------

Use the list endpoint::

    >>> response = browser.get('/v1/admin/petitions')
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": [
        {
          ...
          "dc": {
            "created": "...",
            "effective": null,
            "expires": null,
            "modified": "..."
          },
          ...
          "id": ...,
          ...
          "state": "changed 1",
          ...
        }
      ],
      "total": 1
    }


Delete a Petition
-----------------

Do a delete request::

    >>> response = browser.delete('/v1/admin/petitions/%s' % id)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        ...
        "dc": {
            "created": "...",
            "effective": null,
            "expires": null,
            "modified": "..."
        },
        ...
        "id": ...,
        ...
        "state": "changed 1",
        ...
      }
    }
