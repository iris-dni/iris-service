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

The image proxy URL is provided by the :doc:`files` in the
``image_proxy_base_url`` property. This URL already contains the ``url``
parameter and has to be enhanced with further query parameters and a signature.


Query Parameters
================

The query parameters for the image proxy command are described in the `Pilbox
Documentation <https://github.com/agschwender/pilbox#general-parameters>`_.


Signature
=========

After creating a command with the query parameters, the request has to be signed
with an additional query parameter ``sig``. This is a HMac-SHA1-hashed value
of the previous part of the query parameter.

All parts after the question mark ``?`` have to be used as the ``message`` for
the signing::

    url=/ba1deb533c324cadbe4a8187fed2b5a2&w=200&h=200&mode=crop

The ``passphrase`` is the secret key for signing the request. The secret key
must remain secret. Signed URLs have to be generated backend-side.

Signing with NodeJS using the built-in crypto module::

    var crypto = require("crypto");
    var hmac = crypto.createHmac('sha1', passphrase);
    hmac.write(message);
    hmac.end();
    var signature = hmac.read().hexSlice();
    console.log(signature)

The final URL will look something like this::

    https://imageproxy-iris-dev.lovelysystems.com/?url=/ba1deb533c324cadbe4a8187fed2b5a2&w=200&h=200&mode=crop&sig=7774f8f5c3ea587c7254d0b35c878e2850bc2c7c

Further details on signing can be found in the `Pilbox Signing Documentation
<https://github.com/agschwender/pilbox#signing>`_.


Examples
========

Original
--------

The original image can be fetched by providing the ``op=noop`` parameter::

    http://imageproxy-iris-dev.lovelysystems.com/?url=/bc3168972802460da7af413ffa6125a7&op=noop&sig=1310a4badb3baef1032ea3b52c3c887ad48b005a

.. image:: ./images/pilbox_original.jpeg


Resize
------

Resize an image by providing the width ``w``. The height will be auto-scaled
in the original ratio::

    https://imageproxy-iris-dev.lovelysystems.com/?url=/bc3168972802460da7af413ffa6125a7&w=200&sig=ec187c34eef0cea77dff7b3f676c0ab39339fe2b

.. image:: ./images/pilbox_resized.jpeg


Crop
----

Crop an image by providing width ``w`` and height ``h``::

    http://imageproxy-iris-dev.lovelysystems.com/?url=/bc3168972802460da7af413ffa6125a7&w=200&h=200&sig=53dd4bff091f8b95ca014ddc8c0be93753d5a1eb

.. image:: ./images/pilbox_cropped.jpeg


Region
------

Select a part of the image (region) by using the parameters ``op=resize`` and
``rect=<x>,<y>,<w>,<h>``::

    http://imageproxy-iris-dev.lovelysystems.com/?url=/bc3168972802460da7af413ffa6125a7&op=region&rect=0,0,300,100&sig=a8b1d290707d667d97858776d674f86145adb95b

.. image:: ./images/pilbox_region.jpeg


Cropped region
--------------

First select the region and then crop it to a specific size. Combine the
operator parameters ``op=region,resize`` (order matters!)::

    http://imageproxy-iris-dev.lovelysystems.com/?url=/bc3168972802460da7af413ffa6125a7&op=region,resize&rect=0,0,300,100&h=90&w=160&sig=8027817f0693146cf82f5cc8aba6003ef4e8b119

.. image:: ./images/pilbox_region_cropped.jpeg


.. note::

    The example images are displayed correctly on browsers with large width
    (>950 px).
