================
Petition Service
================

.. contents::


Data
====

.. sourcecode:: json

    {
        "id": ...,
        "dc": {
            ...
        },
        "state": ["signable", "active"],
        "tags": ["domain:aaz", "big"],
        "title": "",
        "city": ref,
        "type": "",
        "description": "",
        "suggested_solution": "",
        "images": [<fileids>],
        "links": [<locations>],
        "videos": [<locations-youtube-only>],
        "connected_locations": [<locations>],
        "signatures": {
            "amount": 32,
            "required": 100
        },
        "owner": "<user-id>",
        "response_token":  "<hashed-id>"
    }


API
===

list
----

.. http:get:: /v1/petitions

    List/filter petitions.

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

    Create new petition. Can be used by anonymous or authenticated users. For
    anonymous users the initial state of the petition is ``draft`` else it is
    ``pending``.


    :<json string city:
        - reference to the city (not required)


Update
------

.. http:put:: /v1/petitions/(integer:id)

    Update existing petition.

    Allowed if
     - petition state is draft
     - and authenticated user is owner

    :<json string city:
        - reference to the city (not required)


Delete
------

.. http:delete:: /v1/petitions/(integer:id)

    Delete a petition.

    ``What is the precondition to be able to delete a petition?``


Sign
----

.. http:post:: /v1/petitions/(integer:id)/sign

    Sign a petition.


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
