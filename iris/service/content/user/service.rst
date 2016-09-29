=============
User Services
=============


Admin API
=========

The admin API is implemented via the REST mapper.

The browser must be logged in with an administrator::

    >>> _ = ssologin(browser, {'email': 'tester@iris.com', 'roles': ['admin']})

Get User List
-------------

Lists all users::

    >>> response = browser.get('/v1/admin/users')
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": [
        {
          "dc": {
            "created": "...",
            "modified": "..."
          },
          "email": "tester@iris.com",
          "email_trusted": false,
          "firstname": "",
          "id": ...,
          "lastname": "",
          "mobile": "",
          "mobile_trusted": false,
          "roles": [
            "admin"
          ],
          "sso": [
            {
              "provider": "local"
            }
          ],
          "state": "active",
          "street": "",
          "town": "",
          "zip": ""
        }
      ],
      "total": 1
    }


Create a User
-------------

Create a new user. The state can not be set::

    >>> user = {
    ...     "data": {
    ...         "state": "test 1",
    ...         "email": "hoschi@galoschi.at",
    ...     }
    ... }
    >>> response = browser.post_json('/v1/admin/users',
    ...                              user)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        "dc": {
          "created": "...",
          "modified": "..."
        },
        "email": "hoschi@galoschi.at",
        ...
        "id": ...,
        ...
        "state": "active",
        ...
      }
    }

    >>> id = response.json['data']['id']


Update a User
-------------

POST on the user with the data which need to be changed::

    >>> user = {
    ...     "data": {
    ...         "email": "hoschi+1@galoschi.at",
    ...         "street": "street 42"
    ...     }
    ... }
    >>> response = browser.post_json('/v1/admin/users/%s' % id,
    ...                              user)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        "dc": {
          "created": "...",
          "modified": "..."
        },
        "email": "hoschi+1@galoschi.at",
        ...
        "id": ...,
        ...
        "street": "street 42",
        ...
      }
    }


Get a User by id
----------------

Use the id from the response above::

    >>> response = browser.get('/v1/admin/users/%s' % id)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        "dc": {
          "created": "...",
          "modified": "..."
        },
        "email": "hoschi+1@galoschi.at",
        ...
        "id": ...,
        ...
      }
    }


List Users
----------

Use the list endpoint::

    >>> response = browser.get('/v1/admin/users')
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": [
        {
          "dc": {
            "created": "...",
            "modified": "..."
          },
          "email": "hoschi+1@galoschi.at",
          ...
          "id": ...,
          ...
        }
      ],
      "total": 2
    }


Delete a User
-------------

Do a delete request::

    >>> response = browser.delete('/v1/admin/users/%s' % id)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        "dc": {
            "created": "...",
            "modified": "..."
        },
        "email": "hoschi+1@galoschi.at",
        ...
        "id": ...,
        ...
      }
    }


Search Filters
==============

Create some sampledata::

    >>> samples.users(5)
    >>> response = browser.get('/v1/admin/users')

Search state::

    >>> response = browser.get('/v1/admin/users?state=disabled')
    >>> print_json(response)
    {
      "data": [
        {
          ...
          "email": "howardtiffany@gmail.com",
          ...
        }
      ],
      "total": 1
    }

Search roles::

    >>> response = browser.get('/v1/admin/users?roles=admin')
    >>> print_json(response)
    {
      "data": [
        {
          ...
          "email": "perezangelica@hotmail.com",
          ...
          "roles": [
            "admin"
          ],
          ...
        },
        {
          ...
          "email": "howardtiffany@gmail.com",
          ...
          "roles": [
            "admin"
          ],
          ...
        },
        {
          ...
          "email": "brianfuller@mcclure-payne.net",
          ...
          "roles": [
            "admin"
          ],
          ...
        }
      ],
      "total": 4
    }

Search email using fulltext search::

    >>> response = browser.get('/v1/admin/users?email_ft=gmail&sort=score')
    >>> print_json(response)
    {
      "data": [
        {
          ...
          "email": "howardtiffany@gmail.com",
          ...
        }
      ],
      "total": 1
    }

Fulltext search::

    >>> response = browser.get('/v1/admin/users?ft=gmail&sort=score')
    >>> print_json(response)
    {
      "data": [
        {
          ...
          "email": "howardtiffany@gmail.com",
          ...
        }
      ],
      "total": 1
    }

    >>> response = browser.get('/v1/admin/users?ft=rich&sort=score')
    >>> print_json(response)
    {
      "data": [
        {
          "dc": {
            "created": "2016-02-12T04:25:09",
            "modified": "2016-02-12T04:25:09"
          },
          "email": "christopher13@conway.com",
          "email_trusted": false,
          "firstname": "Richard",
          "id": ...,
          "lastname": "Cooper",
          "mobile": "",
          "mobile_trusted": false,
          "roles": [],
          "sso": [],
          "state": "active",
          "street": "",
          "town": "",
          "zip": ""
        }
      ],
      "total": 1
    }

    >>> response = browser.get('/v1/admin/users?ft=cooper&sort=score')
    >>> print_json(response)
    {
      "data": [
        {
          "dc": {
            "created": "2016-02-12T04:25:09",
            "modified": "2016-02-12T04:25:09"
          },
          "email": "christopher13@conway.com",
          "email_trusted": false,
          "firstname": "Richard",
          "id": ...,
          "lastname": "Cooper",
          "mobile": "",
          "mobile_trusted": false,
          "roles": [],
          "sso": [],
          "state": "active",
          "street": "",
          "town": "",
          "zip": ""
        }
      ],
      "total": 1
    }


Permissions
===========

Get a test user::

    >>> response = browser.get('/v1/admin/users')
    >>> user_id = response.json['data'][0]['id']

Permission check for all endpoints::

    >>> check_roles("GET", "/v1/admin/users")
    Anonymous                               deny
    Authenticated                           deny
    admin                                   200 OK
    apikey-user                             deny
    session-user                            deny

    >>> check_roles("GET", "/v1/admin/users/%s" % user_id)
    Anonymous                               deny
    Authenticated                           deny
    admin                                   200 OK
    apikey-user                             deny
    session-user                            deny

    >>> def tmp_obj():
    ...     obj = creators.user(email='tester@iris.com')
    ...     return {'obj_id': obj.id}

    >>> check_roles("DELETE", "/v1/admin/users/%(obj_id)s", hook=tmp_obj)
    Anonymous                               deny
    Authenticated                           deny
    admin                                   200 OK
    apikey-user                             deny
    session-user                            deny
