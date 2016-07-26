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
      "state": "draft",
      "suggested_solution": "",
      "supporters": {},
      "tags": [],
      "title": "",
      "type": "",
      "videos": []
    }


API
===

For more information and sample use of the API see
`IRIS-Swagger-UI public petition API </swaggerui#/petition>`_


Manage API
==========

.. _petitions-manage-state:

Manage State
------------

The petiton state machine (see :ref:`petition-management-petition-states`) can
be controlled via events. The event endpoints allow to send the events to a
petition: `IRIS-Swagger-UI event API </swaggerui#/petition_event>`_

The full state machine diagram is shown here: :ref:`petition-management-petition-states`


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
