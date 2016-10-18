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
        "url": "file:///tmp/iris-testing/uploads/..."
      },
      "status": "ok"
    }
    >>> unauth_file_id = response.json['data']['id']

These properties are contained in the data property::

    >>> sorted(response.json['data'].keys())
    [u'content_type', u'id', u'url']

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
    >>> f = File.get(response.json['data']['id'])
    >>> f.owner.id == user.id
    True

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
        "url": "file:///tmp/iris-testing/uploads/..."
      }
    }

These properties are contained in the data property::

    >>> sorted(response.json['data'].keys())
    [u'content_type', u'id', u'url']

An unknown file leads to a 404::

    >>> response = browser.get('/v1/files/unknown', expect_errors=True)
    >>> print response
    Response: 404 Not Found
    ...
    {"error": {"code": 404, "description": "Id 'unknown' for content type 'files' not found"}}


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
        "original_name": "sample.txt",
        "owner": {
          "class": "User",
          "id": "..."
        },
        "state": "visible",
        "storage_type": "tmp",
        "url": "file:///tmp/iris-testing/uploads/..."
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
        "original_name": "iptc.jpeg",
        "owner": {
          "class": "User",
          "id": "..."
        },
        "state": "visible",
        "storage_type": "tmp",
        "url": "file:///tmp/iris-testing/uploads/..."
      }
    }

Users can be resolved with the `resolve=owner` parameter::

    >>> response = browser.get('/v1/admin/files/%s?resolve=owner' % f.id)
    >>> print_json(response.body)
    {
      "data": {
        "content_type": "image/jpeg",
        "dc": {...},
        "id": "...",
        "original_name": "iptc.jpeg",
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
        "state": "visible",
        "storage_type": "tmp",
        "url": "file:///tmp/iris-testing/uploads/..."
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
        "original_name": "iptc.jpeg",
        "owner": {
          "class": "User",
          "id": "..."
        },
        "state": "hidden",
        "storage_type": "tmp",
        "url": "file:///tmp/iris-testing/uploads/..."
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
    1
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

