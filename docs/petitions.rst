================
Petition Service
================

.. contents::


API
===

For more information and sample use of the API see
`IRIS-Swagger-UI public petition API </swaggerui#/petition>`_


.. _petitions-manage-state:

Manage State
============

The petiton state machine (see :ref:`petition-management-petition-states`) can
be controlled via events. The event endpoints allow to send the events to a
petition: `IRIS-Swagger-UI event API </swaggerui#/petition_event>`_

The full state machine diagram is shown here: :ref:`petition-management-petition-states`


Petition Support
================

If a petition is in the state `supportable.*` the properties `dc.effective`
and `dc.expire` are set.

    - `dc.effective`: time when the petition was published
    - `dc.expire`: time when the support time expires (automatic switch to
      next state)
