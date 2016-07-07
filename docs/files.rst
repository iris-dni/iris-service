=============
Files Service
=============

.. contents::


All files are handled as "blobs". There is not special image service.

Files can be uploaded and fetched using the blobs service.

There is no image manipulation included in the IRIS backend. Instead external
services should be used such as `pilbox <http://agschwender.github.io/pilbox/>`_.


Blobs Service
=============


.. http:get:: /v1/blobs/(string:id)

    Download a file.


.. http:post:: /v1/blobs

    Upload a file.

