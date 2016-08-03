===============
City Import API
===============


Permission Settings
===================

The import API needs an API-Key provided in the header::

    >>> from iris.service.security.policy import API_KEY_HEADER_NAME
    >>> API_KEY_HEADER_NAME
    'X-Iris-Api-Key'

    >>> headers = {
    ...     API_KEY_HEADER_NAME: 'local'
    ... }


Create a City
=============

::

    >>> data = {
    ...     "data": [
    ...         {"id": 1007, "name": "aarau"}
    ...     ]
    ... }
    >>> response = browser.post_json('/v1/import/cities', data, headers=headers)
    >>> print_json(response)
    {
      "data": [
        {
          "id": 1007,
          "status": "ok"
        }
      ]
    }

    >>> from iris.service.city import City
    >>> City.get(1007).name
    u'aarau'

Update an existing city
=======================

::

    >>> data = {
    ...     "data": [
    ...         {"id": 1007, "name": "Aarau"}
    ...     ]
    ... }
    >>> response = browser.post_json('/v1/import/cities', data, headers=headers)

    >>> City.get(1007).name
    u'Aarau'


Multiple cities
===============

::

    >>> data = {
    ...     "data": [
    ...         {"id": 1007, "name": "Aarau"},
    ...         {"id": 5004, "name": "Dornbirn"},
    ...     ]
    ... }
    >>> response = browser.post_json('/v1/import/cities', data, headers=headers)
    >>> print_json(response)
    {
      "data": [
        {
          "id": 1007,
          "status": "ok"
        },
        {
          "id": 5004,
          "status": "ok"
        }
      ]
    }

    >>> City.get(1007).name
    u'Aarau'
    >>> City.get(5004).name
    u'Dornbirn'

All Properties::

    >>> data = {
    ...     "data": [
    ...         {
    ...             "id": 1007,
    ...             "name": "Aarau",
    ...             "tags": ["portal:aaz", "kanton:aargau"],
    ...             "zips": ["5004", "5000", "5001"],
    ...             "treshold": 100
    ...         },
    ...     ]
    ... }
    >>> response = browser.post_json('/v1/import/cities', data, headers=headers)
    >>> print_json(response)
    {
      "data": [
        {
          "id": 1007,
          "status": "ok"
        }
      ]
    }
    >>> city = City.get(1007)
    >>> city.name
    u'Aarau'
    >>> city.tags
    [u'portal:aaz', u'kanton:aargau']
    >>> city.zips
    [u'5004', u'5000', u'5001']
    >>> city.treshold
    100
    >>> city.contact
    {}


Edge cases
==========

Empty data list::

    >>> data = {
    ...     "data": [
    ...     ]
    ... }
    >>> response = browser.post_json('/v1/import/cities', data, headers=headers)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": []
    }

Missing id::

    >>> data = {
    ...     "data": [
    ...         {"name": "Aarau"},
    ...         {"id": 5004, "name": "Dornbirn"},
    ...     ]
    ... }
    >>> response = browser.post_json('/v1/import/cities', data, headers=headers)
    >>> print_json(response)
    {
      "data": [
        {
          "status": "missing id"
        },
        {
          "id": 5004,
          "status": "ok"
        }
      ]
    }
