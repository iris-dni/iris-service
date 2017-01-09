============
File Service
============

This document describes the REST APIs to manage files.

Public API
==========

The base route of the public file service is /v1/files.


Uploading a file
----------------

Upload a file using the API::

    >>> import webtest
    >>> import collections
    >>> response = browser.post('/v1/files',
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
        "content_type": "text/plain",
        "id": "...",
        "image_proxy_base_url": "http://imageproxy/?url=/...",
        "info": {},
        "original_url": "file:///tmp/iris-testing/uploads/..."
      },
      "status": "ok"
    }
    >>> unauth_file_id = response.json['data']['id']

These properties are contained in the data property::

    >>> sorted(response.json['data'].keys())
    [u'content_type', u'id', u'image_proxy_base_url', u'info', u'original_url']

A file object containing meta data is stored in the database::

    >>> from iris.service.content.file import File
    >>> f = File.get(response.json['data']['id'])
    >>> print f
    <iris.service.content.file.document.File object at 0x...>

    >>> print f.original_name
    sample.txt

Files are in visible state by default::

    >>> print f.state
    visible

The session user id is stored for unauthenticated users::

    >>> print f.owner.id
    iris-session:...

The user id is stored for authenticated users::

    >>> user = ssologin(browser, {'email': 'someuser@example.com'})
    >>> import os
    >>> here = os.path.dirname(__file__)
    >>> img_file = open(os.path.join(here, "../../testing/blobs/iptc.jpeg"))
    >>> img_content = img_file.read()
    >>> response = browser.post('/v1/files',
    ...                         collections.OrderedDict([
    ...                             ('data', webtest.Upload('iptc.jpeg', img_content))
    ...                         ]))
    >>> image_file_id = response.json['data']['id']
    >>> f = File.get(image_file_id)
    >>> f.owner.id == user.id
    True

The whole file is stored (file pointer resetted to 0)::

    >>> os.path.getsize('/tmp/iris-testing/uploads/%s' % image_file_id)
    858

The file meta data object contains the file's MIME type::

    >>> print f.content_type
    image/jpeg


Get file meta data
------------------

Retrieve a file's meta data by providing the id in the URL::

    >>> response = browser.get('/v1/files/%s' % f.id)
    >>> print response.status
    200 OK
    >>> print_json(response.body)
    {
      "data": {
        "content_type": "image/jpeg",
        "id": "...",
        "image_proxy_base_url": "http://imageproxy/?url=/...",
        "info": {
          "height": 1,
          "width": 1
        },
        "original_url": "file:///tmp/iris-testing/uploads/..."
      }
    }

These properties are contained in the data property::

    >>> sorted(response.json['data'].keys())
    [u'content_type', u'id', u'image_proxy_base_url', u'info', u'original_url']

An unknown file leads to a 404::

    >>> response = browser.get('/v1/files/unknown', expect_errors=True)
    >>> print response
    Response: 404 Not Found
    ...
    {"error": {"code": 404, "description": "Id 'unknown' for content type 'files' not found"}}


Rotated Images
--------------

Helper function to upload file::

    >>> def upload_file(name):
    ...     img_file = open(os.path.join(here, "../../testing/blobs/%s" % name))
    ...     img_content = img_file.read()
    ...     response = browser.post('/v1/files',
    ...                             collections.OrderedDict([
    ...                                 ('data', webtest.Upload(name, img_content))
    ...                             ]))
    ...     return response.json['data']['id']

Upload file with the dimension height=2 and width=1. The file does not have
set the EXIF tag 'Image Orientation' so the dimension is taken as is::

    >>> image_file_id = upload_file('rotated_none.jpeg')
    >>> response = browser.get('/v1/files/%s' % image_file_id)
    >>> response.json['data']['info']
    {u'width': 1, u'height': 2}

Upload file with the dimension height=2 and width=1. The file has set
the EXIF tag 'Image Orientation' to 'Horizontal (normal)' so the dimension is
not toggled::

    >>> image_file_id = upload_file('rotated_0.jpeg')
    >>> response = browser.get('/v1/files/%s' % image_file_id)
    >>> response.json['data']['info']
    {u'width': 1, u'height': 2}

Upload file with the dimension height=2 and width=1. The file has set
the EXIF tag 'Image Orientation' to 'Rotate 90 CW' so the dimension is
toggled::

    >>> image_file_id = upload_file('rotated_90.jpeg')
    >>> response = browser.get('/v1/files/%s' % image_file_id)
    >>> response.json['data']['info']
    {u'width': 2, u'height': 1}

Upload file with the dimension height=2 and width=1. The file has set
the EXIF tag 'Image Orientation' to 'Rotate 180' so the dimension is
not toggled::

    >>> image_file_id = upload_file('rotated_180.jpeg')
    >>> response = browser.get('/v1/files/%s' % image_file_id)
    >>> response.json['data']['info']
    {u'width': 1, u'height': 2}

Upload file with the dimension height=2 and width=1. The file has set
the EXIF tag 'Image Orientation' to 'Rotate 270 CW' so the dimension is
toggled::

    >>> image_file_id = upload_file('rotated_270.jpeg')
    >>> response = browser.get('/v1/files/%s' % image_file_id)
    >>> response.json['data']['info']
    {u'width': 2, u'height': 1}


OPTION requests for CORS
------------------------

CORS is supported for the endpoints::

    >>> response = browser.options('/v1/files')
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

    >>> response = browser.options('/v1/files/something')
    >>> response.status
    '200 OK'


Admin API
=========

The browser must be logged in with an administrator::

    >>> _ = ssologin(browser, {'email': 'tester@iris.com', 'roles': ['admin']})

Uploading a file
----------------

Upload a file using the API::

    >>> response = browser.post('/v1/admin/files',
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
        "content_type": "text/plain",
        "dc": {
          "created": "...",
          "modified": "..."
        },
        "id": "...",
        "image_proxy_base_url": "http://imageproxy/?url=/...",
        "info": {},
        "original_name": "sample.txt",
        "original_url": "file:///tmp/iris-testing/uploads/...",
        "owner": {
          "class": "User",
          "id": "..."
        },
        "state": "visible",
        "storage_type": "tmp"
      },
      "status": "ok"
    }


Get file meta data
------------------

Retrieve a file's meta data by providing the id in the URL::

    >>> response = browser.get('/v1/admin/files/%s' % f.id)
    >>> print response.status
    200 OK
    >>> print_json(response.body)
    {
      "data": {
        "content_type": "image/jpeg",
        "dc": {
          "created": "...",
          "modified": "..."
        },
        "id": "...",
        "image_proxy_base_url": "http://imageproxy/?url=/...",
        "info": {
          "height": 1,
          "width": 1
        },
        "original_name": "iptc.jpeg",
        "original_url": "file:///tmp/iris-testing/uploads/...",
        "owner": {
          "class": "User",
          "id": "..."
        },
        "state": "visible",
        "storage_type": "tmp"
      }
    }

Users can be resolved with the `resolve=owner` parameter::

    >>> response = browser.get('/v1/admin/files/%s?resolve=owner' % f.id)
    >>> print_json(response.body)
    {
      "data": {
        ...
        "owner": {
          "class": "User",
          "data": {
            "dc": {...},
            "email": "someuser@example.com",
            "email_trusted": false,
            "firstname": "",
            "id": "...",
            "lastname": "",
            "mobile": "",
            "mobile_trusted": false,
            "roles": [],
            "salutation": "",
            "sso": [
              {
                "provider": "local"
              }
            ],
            "state": "active",
            "street": "",
            "town": "",
            "zip": ""
          },
          "id": "..."
        },
        ...
      }
    }

Session users can't be resolved, so the data contains null::

    >>> response = browser.get('/v1/admin/files/%s?resolve=owner' % unauth_file_id)
    >>> print_dict(response.json['data']['owner'])
    {
      "class": "User",
      "data": null,
      "id": "iris-session:..."
    }


Update a file's meta data
-------------------------

Update a file's meta data with a POST request and provide the data to be
changed::

    >>> data = {
    ...     "data": {
    ...         "state": "hidden",
    ...         "content_type": "image/gif",
    ...         "url": "readonly"
    ...     }
    ... }
    >>> response = browser.post_json('/v1/admin/files/%s' % f.id, data)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        "content_type": "image/gif",
        "dc": {
          "created": "...",
          "modified": "..."
        },
        "id": "...",
        "info": {
          "height": 1,
          "width": 1
        },
        "original_name": "iptc.jpeg",
        "original_url": "file:///tmp/iris-testing/uploads/...",
        "owner": {
          "class": "User",
          "id": "..."
        },
        "state": "hidden",
        "storage_type": "tmp"
      }
    }


List files
----------

List files with the admin GET endpoint::

    >>> response = browser.get('/v1/admin/files?ft=iptc')
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": [
        {
          ...
          "original_name": "iptc.jpeg",
          ...
        }
      ],
      "total": 1
    }

Sort by owner::

    >>> _ = browser.get('/v1/admin/files?sort=-owner')

Filter by owner::

    >>> response = browser.get('/v1/admin/files?owner=%s' % user.id)
    >>> response.json['total']
    6
    >>> response.json['data'][0]['owner']['id'] == user.id
    True


Delete file
-----------

Delete is currently not supported, as this would require additional tasks like
removing file on S3 and invalidating caches::

    >>> response = browser.delete('/v1/admin/files/%s' % f.id, expect_errors=True)
    >>> print response.status
    400 Bad Request
    >>> print_json(response)
    {
      "errors": {
        "code": "400",
        "description": "Could not find a matching Swagger operation for DELETE request http://localhost/v1/admin/files/..."
      }
    }


OPTION requests for CORS
------------------------

CORS is supported for the endpoints::

    >>> response = browser.options('/v1/admin/files')
    >>> response.status
    '200 OK'


Permissions
===========

    >>> check_roles("POST", "/v1/files")
    Anonymous                               200 OK
    Authenticated                           200 OK
    admin                                   200 OK
    apikey-user                             200 OK
    session-user                            200 OK

    >>> check_roles("GET", "/v1/files/%s" % f.id)
    Anonymous                               200 OK
    Authenticated                           200 OK
    admin                                   200 OK
    apikey-user                             200 OK
    session-user                            200 OK

    >>> check_roles("POST", "/v1/admin/files")
    Anonymous                               deny
    Authenticated                           deny
    admin                                   200 OK
    apikey-user                             deny
    session-user                            deny

    >>> check_roles("GET", "/v1/admin/files/%s" % f.id)
    Anonymous                               deny
    Authenticated                           deny
    admin                                   200 OK
    apikey-user                             deny
    session-user                            deny

