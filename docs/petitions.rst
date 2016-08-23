================
Petition Service
================

.. contents::


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


Support Petitions
-----------------

Petition support is implemented using the `support` event: `IRIS-Swagger-UI event API </swaggerui#/petition_event>`_


Generate Letter
---------------

.. http:post:: /v1/manage/petitions/(string:id)/letter.pdf

    .. sourcecode:: json

        {
            "contact": {
                ...
            }
        }

    ``contact`` overwrites city contact data

    :responseheader Content-Type: application/pdf
