===========
Image Proxy
===========

.. contents::

The image proxy is an independent service to manipulate images in various ways
(e.g. crop or resize images).

The commands and the image URL have to be provided as query parameters and the
whole query string has to be signed to disallow others to penetrate the service.


Base URLs
=========

Each environment has it's own image proxy.

On DEV environment::

    https://imageproxy-iris-dev.lovelysystems.com

On STAGING environment::

    https://imageproxy-iris-stg.lovelysystems.com

On PRODUCTION environment::

    https://images.petition.ch


Query Parameters
================

The general parameters are described in the `Pilbox Documentation
<https://github.com/agschwender/pilbox#general-parameters>`_.

Additional information:

- `url`: The url of the image to be resized. The service is configured to use
  the S3 base URL by default. For images uploaded by the :doc:`files` you
  can skip the hostname and only use the file's ID with a leading slash.
  It's also possible to use images from other locations by providing the
  full URL.
- `client`: The client parameter is required and must contain the value
  ``iris``.


Signature
=========

After creating a command with the query parameters, the request has to be signed
with an additional query parameter ``sig``. This is a HMac-SHA1-hashed value
of the previous part of the query parameter.

All parts after question mark ``?`` have to be used as the ``message`` for the
signing::

    url=/ba1deb533c324cadbe4a8187fed2b5a2&w=200&h=200&mode=crop&client=iris

The ``passphrase`` is the secret key for signing the request. This should not
be provided to users, so the signed URLs should be generated in the (Node)
backend.

Signing with NodeJS using the built-in crypto module::

    var crypto = require("crypto");
    var hmac = crypto.createHmac('sha1', passphrase);
    hmac.write(message);
    hmac.end();
    var signature = hmac.read().hexSlice();
    console.log(signature)

The final URL will look something like this::

    https://imageproxy-iris-dev.lovelysystems.com/?url=/ba1deb533c324cadbe4a8187fed2b5a2&w=200&h=200&mode=crop&client=iris&sig=7149a8fabb37efa11649e0facf37eaf3c806f1d7

Further details on signing can be found in the `Pilbox Signing Documentation
<https://github.com/agschwender/pilbox#signing>`_.


Examples
========

Original
--------

The original image can be fetched by providing the ``op=noop`` parameter::

    http://imageproxy-iris-dev.lovelysystems.com/?url=/bc3168972802460da7af413ffa6125a7&op=noop&client=iris&sig=df705985252dcc9c6e41fae0909fc0fa3f31ee4b

.. image:: ./images/pilbox_original.jpeg


Resize
------

Resize an image by providing the width ``w``. The height will be auto-scaled
in the original ratio::

    https://imageproxy-iris-dev.lovelysystems.com/?url=/bc3168972802460da7af413ffa6125a7&w=200&client=iris&sig=620624f589bf5bede9d4bb2e6d157b9578c010a4

.. image:: ./images/pilbox_resized.jpeg


Crop
----

Crop an image by providing width ``w`` and height ``h``::

    http://imageproxy-iris-dev.lovelysystems.com/?url=/bc3168972802460da7af413ffa6125a7&w=200&h=200&client=iris&sig=305feb4e896b155c2d08b53fb9ba1b443ae612b7

.. image:: ./images/pilbox_cropped.jpeg


Region
------

Select a part of the image (region) by using the parameters ``op=resize`` and
``rect=<x>,<y>,<w>,<h>``::

    http://imageproxy-iris-dev.lovelysystems.com/?url=/bc3168972802460da7af413ffa6125a7&op=region&rect=0,0,300,100&client=iris&sig=baab004acaf1ab9cdba5640ab45fd5dfe8dbadc4

.. image:: ./images/pilbox_region.jpeg


Cropped region
--------------

First select the region and then crop it to a specific size. Combine the
operator parameters ``op=region,resize`` (order matters!)::

    http://imageproxy-iris-dev.lovelysystems.com/?url=/bc3168972802460da7af413ffa6125a7&op=region,resize&rect=0,0,300,100&h=90&w=160&client=iris&sig=3a59dbcb949e0d4eaeaf1b65c1ba07efa4907629

.. image:: ./images/pilbox_region_cropped.jpeg


.. note::

    The example images are displayed correctly on a large browser width (>950 px).
