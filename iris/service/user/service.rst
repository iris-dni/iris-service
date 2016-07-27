=============
User Services
=============


Admin API
=========

The admin API is implemented via the REST mapper.

Get User List
-------------

    >>> response = browser.get('/v1/admin/users')
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": [],
      "total": 0
    }


Create a User
-------------

Create a new user::

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
        "trusted": false
      }
    }

    >>> id = response.json['data']['id']


Update a User
-------------

POST on the user with the data which need to be changed::

    >>> user = {
    ...     "data": {
    ...         "email": "hoschi+1@galoschi.at"
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


List Petitions
--------------

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
      "total": 1
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
    >>> print_json(response)
    {
      "data": [
        {
          "dc": {
            "created": "2016-02-02T11:48:44",
            "modified": "2016-02-02T11:48:44"
          },
          "email": "montoyadaniel@yahoo.com",
          "firstname": "Blake",
          "id": 2,
          "lastname": "Irwin",
          "roles": [],
          "sso": [
            {
              "provider": "zeitOnline",
              "trusted": false
            }
          ],
          "state": "active",
          "trusted": false
        },
        {
          "dc": {
            "created": "2016-02-12T04:25:09",
            "modified": "2016-02-12T04:25:09"
          },
          "email": "christopher13@conway.com",
          "firstname": "Richard",
          "id": 3,
          "lastname": "Cooper",
          "roles": [],
          "sso": [],
          "state": "active",
          "trusted": false
        },
        {
          "dc": {
            "created": "2016-02-13T13:50:55",
            "modified": "2016-02-13T13:50:55"
          },
          "email": "perezangelica@hotmail.com",
          "firstname": "Terri",
          "id": 4,
          "lastname": "Woodward",
          "roles": [
            "admin"
          ],
          "sso": [
            {
              "provider": "azMedien",
              "trusted": false
            }
          ],
          "state": "active",
          "trusted": false
        },
        {
          "dc": {
            "created": "2016-04-02T09:32:50",
            "modified": "2016-04-02T09:32:50"
          },
          "email": "howardtiffany@gmail.com",
          "firstname": "Adam",
          "id": 5,
          "lastname": "Jackson",
          "roles": [
            "admin"
          ],
          "sso": [
            {
              "provider": "zeitOnline",
              "trusted": false
            }
          ],
          "state": "disabled",
          "trusted": false
        },
        {
          "dc": {
            "created": "2016-04-30T16:04:48",
            "modified": "2016-04-30T16:04:48"
          },
          "email": "brianfuller@mcclure-payne.net",
          "firstname": "Sherry",
          "id": 6,
          "lastname": "Hernandez",
          "roles": [
            "admin"
          ],
          "sso": [
            {
              "provider": "azMedien",
              "trusted": true
            }
          ],
          "state": "active",
          "trusted": false
        }
      ],
      "total": 5
    }

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
      "total": 3
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
          "firstname": "Richard",
          "id": 3,
          "lastname": "Cooper",
          "roles": [],
          "sso": [],
          "state": "active",
          "trusted": false
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
          "firstname": "Richard",
          "id": 3,
          "lastname": "Cooper",
          "roles": [],
          "sso": [],
          "state": "active",
          "trusted": false
        }
      ],
      "total": 1
    }
