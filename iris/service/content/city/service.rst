=============
City Services
=============


Admin API
=========

The admin API is implemented via the REST mapper.

The browser must be logged in with an administrator::

    >>> _ = ssologin(browser, {'email': 'tester@iris.com', 'roles': ['admin']})


Get City List
-------------

Lists all cities::

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
    ...         "id": "10042",
    ...         "provider": "test",
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
        "id": "test:10042",
        "name": "aarau",
        "provider": "test",
        "state": "active",
        "tags": [
          "portal:aaz"
        ],
        "treshold": -1,
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
        "id": "test:10042",
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
        "contact": {},
        "dc": {
          "created": "...",
          "modified": "..."
        },
        "id": "test:10042",
        "name": "Aarau",
        "provider": "test",
        "state": "active",
        "tags": [
          "portal:aaz"
        ],
        "treshold": -1,
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


Permissions
===========

Get a test city::

    >>> response = browser.get('/v1/admin/cities')
    >>> city_id = response.json['data'][0]['id']

Permission check for all endpoints::

    >>> check_roles("GET", "/v1/admin/cities")
    Anonymous                               deny
    Authenticated                           deny
    admin                                   200 OK
    apikey-user                             deny
    session-user                            deny

    >>> check_roles("GET", "/v1/admin/cities/%s" % city_id)
    Anonymous                               deny
    Authenticated                           deny
    admin                                   200 OK
    apikey-user                             deny
    session-user                            deny

    >>> def tmp_city():
    ...     city = creators.city(id='1111',
    ...                          provider='check_roles',
    ...                          name='tester')
    ...     return {'city_id': city.id}

    >>> check_roles("DELETE", "/v1/admin/cities/%(city_id)s", hook=tmp_city)
    Anonymous                               deny
    Authenticated                           deny
    admin                                   200 OK
    apikey-user                             deny
    session-user                            deny
