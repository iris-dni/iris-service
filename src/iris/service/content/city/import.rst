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
    ...         {
    ...             "operation": "add",
    ...             "data": {"id": "1007", "name": "aarau"}
    ...         }
    ...     ]
    ... }
    >>> response = browser.post_json('/v1/import/cities', data, headers=headers)
    >>> print_json(response)
    {
      "data": [
        {
          "id": "1007",
          "irisId": "local:1007",
          "status": "ok:added"
        }
      ]
    }

    >>> from iris.service.content.city import City
    >>> City.get('local:1007').name
    u'aarau'


Update an existing city
=======================

::

    >>> data = {
    ...     "data": [
    ...         {
    ...             "operation": "update",
    ...             "data": {"id": "1007", "name": "Aarau"}
    ...         }
    ...     ]
    ... }
    >>> response = browser.post_json('/v1/import/cities', data, headers=headers)

    >>> City.get('local:1007').name
    u'Aarau'


Multiple cities
===============

::

    >>> data = {
    ...     "data": [
    ...         {
    ...             "operation": "update",
    ...             "data": {"id": "1007", "name": "Aarau"},
    ...         },
    ...         {
    ...             "operation": "update",
    ...             "data": {"id": "5004", "name": "Dornbirn"},
    ...         }
    ...     ]
    ... }
    >>> response = browser.post_json('/v1/import/cities', data, headers=headers)
    >>> print_json(response)
    {
      "data": [
        {
          "id": "1007",
          "irisId": "local:1007",
          "status": "ok:updated"
        },
        {
          "id": "5004",
          "irisId": "local:5004",
          "status": "ok:added"
        }
      ]
    }

    >>> City.get("local:1007").name
    u'Aarau'
    >>> City.get("local:5004").name
    u'Dornbirn'

All Properties::

    >>> data = {
    ...     "data": [
    ...         {
    ...             "operation": "update",
    ...             "data": {
    ...                 "id": "1007",
    ...                 "name": "Aarau",
    ...                 "tags": ["portal:aaz", "kanton:aargau"],
    ...                 "zips": ["5004", "5000", "5001"],
    ...                 "geopos": None,
    ...                 "location": {"url": "https://www.aargauerzeitung.ch"},
    ...                 "portal": {
    ...                     "id": "nwch:1007",
    ...                     "rss2": "https://www.aargauerzeitung.ch/gemeinde/urlpart-1007/rss.xml",
    ...                     "title": "Aargauer Zeitung"
    ...                 },
    ...                 "treshold": 100
    ...             }
    ...         },
    ...     ]
    ... }
    >>> response = browser.post_json('/v1/import/cities', data, headers=headers)
    >>> print_json(response)
    {
      "data": [
        {
          "id": "1007",
          "irisId": "local:1007",
          "status": "ok:updated"
        }
      ]
    }
    >>> city = City.get("local:1007")
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
    >>> pprint(city.portal)
    {u'id': u'nwch:1007',
     u'rss2': u'https://www.aargauerzeitung.ch/gemeinde/urlpart-1007/rss.xml',
     u'title': u'Aargauer Zeitung'}
    >>> city.location
    <RelationResolver WebLocation[9badb72136e94347c3caf7a37e4f7947]>


Delete a City
=============

::

    >>> data = {
    ...     "data": [
    ...         {
    ...             "operation": "delete",
    ...             "data": {"id": "1007"},
    ...         },
    ...         {
    ...             "operation": "delete",
    ...             "data": {"id": "33267"},
    ...         },
    ...         {
    ...             "operation": "update",
    ...             "data": {"id": "5004", "name": "Dornbirn"},
    ...         }
    ...     ]
    ... }
    >>> response = browser.post_json('/v1/import/cities', data, headers=headers)
    >>> print_json(response)
    {
      "data": [
        {
          "id": "1007",
          "irisId": "local:1007",
          "status": "ok:deleted"
        },
        {
          "id": "33267",
          "status": "error:not_found"
        },
        {
          "id": "5004",
          "irisId": "local:5004",
          "status": "ok:updated"
        }
      ]
    }

    >>> City.get("local:1007") is None
    True


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
    ...         {"operation": "update", "data": {"name": "Aarau"}},
    ...         {"operation": "update", "data": {"id": "5004", "name": "Dornbirn"}},
    ...     ]
    ... }
    >>> response = browser.post_json('/v1/import/cities', data, headers=headers)
    >>> print_json(response)
    {
      "data": [
        {
          "status": "error:missing_id"
        },
        {
          "id": "5004",
          "irisId": "local:5004",
          "status": "ok:updated"
        }
      ]
    }
