============
City Service
============

.. contents::


Data
====

.. sourcecode:: json

    {
        "id": 1234,
        "status": "published",
        "tags": ["domain:aaz", "big"],
        "name": "",
        "zips": ["123", "456"],
        "inhabitants": 12543,
        "contact": {
            "salutation": "Sehr geehrter Herr Stromberg",
            "address": "Bahnhofstrasse 1, D - 0815 Finsdorf"
        }
    }


City Data Import
================

.. http:post:: /v1/cities/import

    Allows to post cities to the city service. This is the only way to create
    new cities.

    **Example Request**

    Prepare the JSON POST body with the city list:

    .. sourcecode:: python

        >>> citydata = [
        ...     {
        ...         "id": 1234,
        ...         "tags": ["domain:aaz", "big"],
        ...         "name": "Aarau",
        ...         "zips": ["5004"],
        ...         "inhabitants": 12543
        ...     },
        ...     {
        ...         "id": 5678,
        ...         "tags": ["small"],
        ...         "inhabitants": 67
        ...     },
        ...     {
        ...         "id": 42,
        ...         "__delete__": True
        ...     },
        ...     {
        ...         "tags": ["error"]
        ...     }
        ... ]

    Call the import API with the city list:

    >>> HTTP_POST_JSON('/v1/cities/import', citydata)
    {
        "status": [
            {
                "status": "created"
            },
            {
                "status": "updated"
            },
            {
                "status": "deleted"
            },
            {
                "status": "error",
                "code": 57,
                "description": "missing 'id'"
            }
        ]
    }

    :requestheader X-Iris-Api-Key:
        - the API key must be provided to be able to get access to this endpoint

    :responseheader Content-Type: application/json


Management API
==============

The management endpoints are only available with a valid authentication.

.. http:get:: /v1/manage/cities

    List/Filter cities.


.. http:get:: /v1/manage/cities/(string:id)

    Provides data for a specific city.

    **Example request**

    >>> HTTP_GET_JSON('/v1/manage/cities/1234')
    {
        "id": 1234,
        "tags": ["domain:aaz", "big"],
        "inhabitants": 12543,
        "contact": {
            "salutation": "Sehr geehrter Herr Stromberg",
            "address": "Bahnhofstrasse 1, D - 0815 Finsdorf"
        }
    }

    :responseheader Content-Type: application/json

    :param int/string id:
        - the id of the city

.. http:post:: /v1/manage/cities/(string:id)

    Update a city.

    Allowed fields:
        - contact.salutation
        - contact.address

    **Example Request**

    Prepare the JSON POST body with the fields:

    .. sourcecode:: python

        >>> citydata = {
        ...     "contact": {
        ...         "salutation": "",
        ...         "address": "",
        ...     }
        ... }

    Call the import API with the city list:

    >>> HTTP_POST_JSON('/v1/cities/12345', citydata)
    {
        "status": "ok"
    }

    :responseheader Content-Type: application/json


.. http:delete:: /v1/manage/cities/(string:id)

    Delete a specific city.

    **Example Request**

    >>> HTTP_DELETE_JSON('/v1/cities/12345')
    {
        "status": "ok"
    }
