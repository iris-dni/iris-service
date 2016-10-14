=============
Files Service
=============

.. contents::


All files are handled as "blobs". There is no special image service.

Files can be uploaded and fetched using the blobs service.

There is no image manipulation included in the IRIS backend. Instead external
services should be used such as `pilbox <http://agschwender.github.io/pilbox/>`_.


Blobs Service
=============

The service is described here: `IRIS-Swagger-UI blobs API </swaggerui#/blob>`_

.. http:get:: /v1/blobs/(string:id)

    Download a file.

.. doctest::
    :hide:

    >>> import webtest
    >>> import collections

.. http:post:: /v1/blobs

    Upload a file.

    See `Multipart/Form-Data documentation on W3C
    <https://www.w3.org/TR/html401/interact/forms.html#h-17.13.4.2>`_
    for more information on how to provide the file data.

    **Example request**

    .. sourcecode:: python

        >>> upload_form = collections.OrderedDict([
        ...     ('data', webtest.Upload('sample.txt', 'some_file_content'))
        ... ])
        >>> response = browser.post('/v1/blobs', upload_form)
        >>> print_json(response.body)
        {
          "data": {
            "id": "..."
          },
          "status": "ok"
        }

