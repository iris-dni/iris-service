=============
City Services
=============


Admin API
=========

The admin API is implemented via the REST mapper.

Get City List
-------------

    >>> response = browser.get('/v1/admin/cities')
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": [],
      "total": 0
    }


Create a City
-------------

Create a new city::

    >>> city = {
    ...     "data": {
    ...         "name": "aarau",
    ...         "tags": ["portal:aaz"],
    ...         "zips": ["5004"],
    ...     }
    ... }
    >>> response = browser.post_json('/v1/admin/cities',
    ...                              city)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        "contact": {},
        "dc": {
          "created": "...",
          "modified": "..."
        },
        "id": ...,
        "name": "aarau",
        "state": "active",
        "tags": [
          "portal:aaz"
        ],
        "treshold": 0,
        "zips": [
          "5004"
        ]
      }
    }

    >>> id = response.json['data']['id']


Update a City
-------------

POST on the city with the data which need to be changed::

    >>> city = {
    ...     "data": {
    ...         "name": "Aarau"
    ...     }
    ... }
    >>> response = browser.post_json('/v1/admin/cities/%s' % id,
    ...                              city)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        ...
        "name": "Aarau",
        ...
      }
    }


Get a City by id
----------------

Use the id from the response above::

    >>> response = browser.get('/v1/admin/cities/%s' % id)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        ...
        "dc": {
          "created": "...",
          "modified": "..."
        },
        ...
        "name": "Aarau",
        "state": "active",
        "tags": [
          "portal:aaz"
        ],
        "treshold": 0,
        "zips": [
          "5004"
        ]
      }
    }


List Petitions
--------------

Use the list endpoint::

    >>> response = browser.get('/v1/admin/cities')
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": [
        {
          ...
          "dc": {
            "created": "...",
            "modified": "..."
          },
          ...
          "name": "Aarau",
          ...
        }
      ],
      "total": 1
    }


Delete a City
-------------

Do a delete request::

    >>> response = browser.delete('/v1/admin/cities/%s' % id)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        ...
        "dc": {
            "created": "...",
            "modified": "..."
        },
        ...
        "name": "Aarau",
        ...
      }
    }


Search
======

Create some sampledata::

    >>> samples.cities(10)
    >>> response = browser.get('/v1/admin/cities')


Filter by Tags
--------------

Search results can be filtered by tags::

    >>> response = browser.get('/v1/admin/cities?tags=portal:aaz')
    >>> print_json(response)
    {
      "data": [
        {
          ...
          "tags": [
            "portal:aaz"
          ],
          ...
      ],
      "total": 5
    }

It is possible to provide multiple tags::

    >>> response = browser.get('/v1/admin/cities?tags=portal:gtb,portal:aaz')
    >>> print_json(response)
    {
      "data": [
        {
          ...
        }
      ],
      "total": 7
    }


General Fulltext Search
-----------------------

Uses all existing fulltext fields::

    >>> response = browser.get('/v1/admin/cities?ft=brookestad&sort=score')
    >>> print_json(response)
    {
      "data": [
        {
    ...
        }
      ],
      "total": 3
    }
