============
File Service
============

This document describes the REST API to manage blobs.

Blobs (Binary large objects) get used for plain files like images and so
on. The base route of the blobs service is /v1/blobs.


Uploading a blob
================

Upload a file using the API::

    >>> import webtest
    >>> import collections
    >>> response = browser.post('/v1/blobs',
    ...                         collections.OrderedDict([
    ...                             ('data', webtest.Upload('sample.txt', 'sample'))
    ...                         ]))
    >>> print response
    Response: 200 OK
    ...
    Content-Type: application/json; charset=UTF-8
    ...

    >>> print_json(response.body)
    {
      "data": {
        "id": "..."
      },
      "status": "ok"
    }

A file object containing meta data is stored in the database::

    >>> from iris.service.content.file import File
    >>> f = File.get(response.json['data']['id'])
    >>> print f
    <iris.service.content.file.document.File object at 0x...>

    >>> print f.original_name
    sample.txt

Blobs are in visible state by default::

    >>> print f.state
    visible

The session user id is stored for unauthenticated users::

    >>> print f.owner_id
    iris-session:...

The user id is stored for authenticated users::

    >>> user = ssologin(browser, {'email': 'someuser@example.com'})
    >>> import os
    >>> here = os.path.dirname(__file__)
    >>> img_file = open(os.path.join(here, "../../testing/blobs/iptc.jpeg"))
    >>> img_content = img_file.read()
    >>> response = browser.post('/v1/blobs',
    ...                         collections.OrderedDict([
    ...                             ('data', webtest.Upload('iptc.jpeg', img_content))
    ...                         ]))
    >>> f = File.get(response.json['data']['id'])
    >>> f.owner_id == user.id
    True

The file meta data object contains the file's MIME type::

    >>> print f.content_type
    image/jpeg


Permissions
-----------

    >>> check_roles("POST", "/v1/blobs")
    Anonymous                               200 OK
    Authenticated                           200 OK
    admin                                   200 OK
    apikey-user                             200 OK
    session-user                            200 OK


Retrieve a blob
===============

Retrieve a blob by providing the id in the URL::

    >>> response = browser.get('/v1/blobs/%s' % f.id)
    >>> print response.status
    200 OK

The MIME type is used from the file's meta data::

    >>> print response.content_type
    image/jpeg

    >>> print response.charset
    UTF-8
    >>> print response.cache_control
    max-age=86400
    >>> response.body == img_content
    True

An unknown blob leads to a 404::

    >>> response = browser.get('/v1/blobs/unknown', expect_errors=True)
    >>> print response
    Response: 404 Not Found
    ...
    {"error": {"code": 404, "description": "Id 'unknown' for content type 'blob' not found"}}


Permissions
-----------

    >>> check_roles("GET", "/v1/blobs/%s" % f.id)
    Anonymous                               200 OK
    Authenticated                           200 OK
    admin                                   200 OK
    apikey-user                             200 OK
    session-user                            200 OK


OPTION requests for CORS
========================

CORS is supported for the endpoints::

    >>> response = browser.options('/v1/blobs')
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {}
    >>> print_json({n: v for n,v in response.headers.items() if n.startswith('Access')})
    {
      "Access-Control-Allow-Credentials": "true",
      "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization",
      "Access-Control-Allow-Methods": "POST,GET,DELETE,PUT,OPTIONS",
      "Access-Control-Allow-Origin": "http://localhost",
      "Access-Control-Max-Age": "86400"
    }

    >>> response = browser.options('/v1/blobs/something')
    >>> response.status
    '200 OK'

