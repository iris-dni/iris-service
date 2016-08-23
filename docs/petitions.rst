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


Support Petitions
=================

Petition support is implemented using the `support` event: `IRIS-Swagger-UI event API </swaggerui#/petition_event/support>`_

This event requires a JSON body with the identification of the supporting
user. This can be provided in two ways:

- logged in user (SSO)
- phone_user
  The `phone_user` is a user which was identified using his phone number. The
  `phone_user` must be provided as an object with these properties:
  - telephone (required)
  - firstname
  - lastname
