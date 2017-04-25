===
API
===

.. contents::


.. doctest::
    :hide:

    >>> samples.users(10)
    >>> samples.cities(10)
    >>> samples.petitions(10)


Relation Handling
=================

All data API's allow the additional query parameter ``resolve``. This
parameter specifies which relations of a documents should be expanded for the
response.

Relations are always represented as an object.

.. sourcecode:: json

    {
        "id": "...",
        "class": "..."
    }

.. http:get:: /v1/petitions?resolve=city,owner

    The query parameter ``resolve`` will provide the city and the owner
    property of the petitions to contain the full data of the document.

    **Example request without resolve**

    .. sourcecode:: python

        >>> HTTP_GET_JSON('/v1/petitions')
        {
          "data": [
            {
              "city": {
                "class": "City",
                "id": ...
              },
              ...
            },
            ...
          ],
          ...
        }

    **Example request with resolve**

    .. sourcecode:: python

        >>> HTTP_GET_JSON('/v1/petitions?resolve=city')
        {
          "data": [
            {
              "city": {
                "class": "City",
                "data": {
                  "geopos": null,
                  "id": "...",
                  "location": {
                    "class": "WebLocation",
                    "id": null
                  },
                  "name": "Brookestad",
                  "portal": {},
                  "provider": "test",
                  "tags": [
                    "portal:aaz"
                  ],
                  "treshold": 10,
                  "zips": [
                    "22679"
                  ]
                },
                "id": ...
              },
              ...
            },
            ...
          ],
          ...
        }
