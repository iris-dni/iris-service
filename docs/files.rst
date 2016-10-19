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

    >>> import webtest
    >>> import collections


.. http:post:: /v1/files

    Upload a file.

    See `Multipart/Form-Data documentation on W3C
    <https://www.w3.org/TR/html401/interact/forms.html#h-17.13.4.2>`_
    for more information on how to provide the file data.

    **Example request**

    .. sourcecode:: python

        >>> upload_form = collections.OrderedDict([
        ...     ('data', webtest.Upload('sample.txt', 'some_file_content'))
        ... ])
        >>> response = browser.post('/v1/files', upload_form)
        >>> print_json(response.body)
        {
          "data": {
            "content_type": "text/plain",
            "id": "...",
            "url": "file:///tmp/iris-testing/uploads/..."
          },
          "status": "ok"
        }

.. http:get:: /v1/files/(string:id)

    GET a file's meta data.

    To download the real file use the provided `url` in the `data` object. The
    file is currently downloaded from S3.

    Use the :doc:`imageproxy` to fetch image files.

    .. sourcecode:: python

        >>> id = response.json['data']['id']
        >>> HTTP_GET_JSON('/v1/files/%s' % id)
        {
          "data": {
            "content_type": "text/plain",
            "id": "...",
            "url": "file:///tmp/iris-testing/uploads/..."
          }
        }