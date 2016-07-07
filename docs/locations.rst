================
Location Service
================

.. contents::

Locations point to URLs and provide og information about the location to be
able to render a representation og the location.

Locations are created when they are needed based on other data e.g. petition
links.

For new locations a page request is triggered to extract og data. The
extracted og data is stored on the location object.


Data
====

.. sourcecode:: json

    {
        "id": "short",
        "status": "published",
        "url": "",
        "og": {
            "image": "",
            "title": "",
            ...
        }
    }


Management API
==============

The management endpoints are only available with a valid authentication.

.. http:get:: /v1/manage/locations

    List and filter locations.

    **Example request**

    >>> HTTP_GET_JSON('/v1/manage/locations')

.. http:get:: /v1/manage/locations/(string:id)

    Provides a specific location.

    **Example request**

    >>> HTTP_GET_JSON('/v1/manage/locations/short')

.. http:post:: /v1/manage/locations/(string:id)

    Allows to change the status of a location.

    **Example request**

    .. sourcecode:: python

        >>> locationData = {
        ...     "status": "draft"
        ... }

    >>> HTTP_POST_JSON('/v1/manage/locations/short', locationData)
    {
        "status": "updated"
    }
