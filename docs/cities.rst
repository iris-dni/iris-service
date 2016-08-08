============
City Service
============

.. contents::


Importer
========

The import allows to create, edit and delete cities in IRIS.

The city import API is decribed here: `IRIS-Swagger-UI city import API </swaggerui#/city_import>`_

The import endpoint must be called with a valid application key provided in
the request header `X-Iris-Api-Key`.


City Ids
--------

The id of a city must be provided when importing a city. The id must be a
string.

To be able to manage multiple city sources the internal city id is a prefixed
version of the external id. The prfix is the provider which is defined
internally via the apikey.


Administration Endpoints
========================

User management is available via these endpoints: `IRIS-Swagger-UI city admin API </swaggerui#/city_admin>`_
