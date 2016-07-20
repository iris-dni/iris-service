================
Petition Service
================

.. contents::

.. doctest::
    :hide:

    >>> petition_42 = creators.petition(id=42)


Petition Data
=============

.. sourcecode:: json

    >>> pp(petition_42.get_source())
    {
      "city": null,
      "connected_locations": [],
      "dc": {
        "created": "...",
        "effective": null,
        "expires": null,
        "modified": "..."
      },
      "description": "",
      "id": 42,
      "images": [],
      "links": [],
      "owner": null,
      "response_token": null,
      "supporters": {},
      "state": "draft",
      "suggested_solution": "",
      "tags": [],
      "title": "",
      "type": "",
      "videos": []
    }


API
===

list
----

.. http:get:: /v1/petitions

    List/filter petitions.

    **example request**

    .. sourcecode:: json

        >>> HTTP_GET_JSON('/v1/petitions')
        {
          "data": [
            {
              ...
              "id": 42,
              ...
            }
          ],
          "total": 1
        }

    :resheader Content-Type: application/json

    :statuscode 200: no error

    :param string city_id:
        - filter by city id
    :param string state:
        - filter by state(s), provide multiple states as comma separated list
    :param string city_tag:
        - filter by city_tag(s), provide multiple tags as comma separated list
    :param string owner:
        - filter by owner
    :param string ft:
        - fulltext filter

            - contains: title, description

    :param string sort:
        - sort by

            - published
            - ``trending ???``


Create
------

.. http:post:: /v1/petitions

    Create new petition. The new petition is always in state ``draft``.

    **example request**

    .. sourcecode:: json

        >>> petition = {
        ...     "data": {
        ...         "title": "my petition",
        ...         "description": "All about my petition",
        ...         "type": "i don't like",
        ...         "images": ["the_image_hash"]
        ...     }
        ... }
        >>> HTTP_POST_JSON('/v1/petitions', petition)
        {
          "data": {
            "city": null,
            "connected_locations": [],
            "dc": {
              ...
            },
            "description": "All about my petition",
            "id": 1,
            "images": [
              "the_image_hash"
            ],
            "links": [],
            "owner": null,
            "response_token": null,
            "supporters": {},
            "state": "draft",
            "suggested_solution": "",
            "tags": [],
            "title": "my petition",
            "type": "i don't like",
            "videos": []
          }
        }

    :resheader Content-Type: application/json

    :statuscode 201: created

    :<json string city:
        - reference to the city (not required)


Update
------

.. http:put:: /v1/petitions/(integer:id)

    Update existing petition.

    The petition must be ``draft`` and the current user is the owner of the
    petition or an editor.

    **example request**

    .. sourcecode:: json

        >>> petition = {
        ...     "data": {
        ...         "title": "better title",
        ...     }
        ... }
        >>> HTTP_POST_JSON('/v1/petitions/1', petition)
        {
          "data": {
            ...
            "id": 1,
            ...
            "title": "better title",
            ...
          }
        }

    :resheader Content-Type: application/json

    :statuscode 200: modified
    :statuscode 404: petition not found

    :<json string city:
        - reference to the city (not required)


Delete
------

.. http:delete:: /v1/petitions/(integer:id)

    Delete a petition.

    ``What is the precondition to be able to delete a petition?``

    **example request**

    .. sourcecode:: json

        >>> HTTP_DELETE_JSON('/v1/petitions/1')
        {
          "data": {
            ...
            "id": 1,
            ...
          }
        }

    :resheader Content-Type: application/json

    :statuscode 200: deleted
    :statuscode 404: petition not found


Support
-------

.. http:post:: /v1/petitions/(integer:id)/support

    Support a petition.

    **example request**

    .. sourcecode:: json

        >>> data = {
        ...     "data": {
        ...         "name": "ma name"
        ...     }
        ... }
        >>> HTTP_POST_JSON('/v1/petitions/42/support', data)
        {}

    :resheader Content-Type: application/json

    :statuscode 200: supported
    :statuscode 404: petition not found
    :statuscode 400: details are in the json response body


Add City Response
-----------------

.. http:post:: /v1/petitions/(string:token)/add_city_response

    Unauthenticated use.

    Current state is ``waitForLetterResponse``.

    Set new state to ``letterResponseArrived``.

    .. sourcecode:: json

        {
            "feedback": "..."
        }


Manage API
==========

Switch State
------------

.. http:post:: /v1/manage/petitions/(string:id)/switch_state


Generate Letter
---------------

.. http:post:: /v1/manage/petitions/(string:id)/generate_letter_pdf

    .. sourcecode:: json

        {
            "contact": {
                ...
            }
        }

    ``contact`` overwrites city contact data

    :responseheader Content-Type: application/pdf


Notifications
=============

TODO
