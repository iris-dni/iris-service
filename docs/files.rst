=============
Files Service
=============

.. contents::


All files are handled as "blobs". There is no special image service.

Files can be uploaded and fetched using the files service.

There is no image manipulation included in the IRIS backend. Instead external
services should be used such as `pilbox <http://agschwender.github.io/pilbox/>`_.


File Service
============

The service is described here: `IRIS-Swagger-UI files API </swaggerui#/file>`_

.. doctest::
    :hide:

    >>> import os
    >>> import webtest
    >>> import collections
    >>> here = os.path.dirname(__file__)
    >>> img_file = open(os.path.join(here, "../iris/service/testing/blobs/iptc.jpeg"))
    >>> image_content = img_file.read()


.. http:post:: /v1/files

    Upload a file.

    See `Multipart/Form-Data documentation on W3C
    <https://www.w3.org/TR/html401/interact/forms.html#h-17.13.4.2>`_
    for more information on how to provide the file data.

    **Example request**

    .. sourcecode:: python

        >>> upload_form = collections.OrderedDict([
        ...     ('data', webtest.Upload('image.jpeg', image_content))
        ... ])
        >>> response = browser.post('/v1/files', upload_form)
        >>> print_json(response.body)
        {
          "data": {
            "content_type": "image/jpeg",
            "id": "...",
            "image_proxy_base_url": "http://imageproxy/?url=...",
            "info": {
              "height": 1,
              "width": 1
            },
            "original_url": "file:///tmp/iris-testing/uploads/..."
          },
          "status": "ok"
        }

.. http:get:: /v1/files/(string:id)

    GET a file's meta data.

    To download the original file use the provided `original_url` in the `data`
    object.

    The ``info`` property may contain additional data about the file. Valid
    image files contain the properties ``height`` and ``width``.

    To fetch `image` files and possibly resize or crop them, use the
    :doc:`imageproxy` by enhancing the ``image_proxy_base_url``.

    .. sourcecode:: python

        >>> id = response.json['data']['id']
        >>> HTTP_GET_JSON('/v1/files/%s' % id)
        {
          "data": {
            "content_type": "image/jpeg",
            "id": "...",
            "image_proxy_base_url": "http://imageproxy/?url=...",
            "info": {
              "height": 1,
              "width": 1
            },
            "original_url": "file:///tmp/iris-testing/uploads/..."
          }
        }