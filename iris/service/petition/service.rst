=================
Petition Services
=================


Public API
==========

The public API contains the endpoints which are available for the frontend.


Create Petition
---------------

    >>> petition = {
    ...     "data": {
    ...         "state": {"name": "test"},
    ...         "title": "Public petition"
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        ...
        "dc": {
          "created": "...",
          "effective": null,
          "expires": null,
          "modified": "..."
        },
        ...
        "id": ...,
        ...
        "state": {
          "name": "draft",
          "parent": ""
        },
        ...
      }
    }

    >>> id = response.json['data']['id']


Get Petition
------------

    >>> response = browser.get('/v1/petitions/%s' % id)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        ...
        "dc": {
          "created": "...",
          "effective": null,
          "expires": null,
          "modified": "..."
        },
        ...
        "id": ...,
        ...
        "state": {
          "name": "draft",
          "parent": ""
        },
        ...
      }
    }


Delete Petition
---------------

    >>> response = browser.delete('/v1/petitions/%s' % id)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        ...
        "dc": {
          "created": "...",
          "effective": null,
          "expires": null,
          "modified": "..."
        },
        ...
        "id": ...,
        ...
      }
    }

    >>> response = browser.get('/v1/petitions/%s' % id, expect_errors=True)
    >>> response.status
    '404 Not Found'


OPTION requests for CORS
------------------------

CORS is supported for all endpoints::

    >>> response = browser.options('/v1/petitions')
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

    >>> response = browser.options('/v1/petitions/1')
    >>> response.status
    '200 OK'


Admin API
=========

The admin API is implemented via the REST mapper.

The browser must be logged in with an administrator::

    >>> _ = ssologin(browser, {'email': 'tester@iris.com', 'roles': ['admin']})

Get Petition List
-----------------

    >>> response = browser.get('/v1/admin/petitions')
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": [],
      "total": 0
    }


Create a Petition
-----------------

Create a new petition::

    >>> petition = {
    ...     "data": {
    ...         "state": {"name": "test 1"},
    ...         "title": "Admin petition",
    ...     }
    ... }
    >>> response = browser.post_json('/v1/admin/petitions',
    ...                              petition)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        ...
        "dc": {
          "created": "...",
          "effective": null,
          "expires": null,
          "modified": "..."
        },
        ...
        "id": ...,
        ...
        "state": {
          "listable": false,
          "name": "draft",
          "parent": "",
          "timer": 0
        },
        ...
        "title": "Admin petition",
        ...
      }
    }

    >>> id = response.json['data']['id']


Update a Petition
-----------------

POST on the petition with the data which need to be changed::

    >>> petition = {
    ...     "data": {
    ...         "title": "changed Admin petition"
    ...     }
    ... }
    >>> response = browser.post_json('/v1/admin/petitions/%s' % id,
    ...                              petition)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        ...
        "dc": {
          "created": "...",
          "effective": null,
          "expires": null,
          "modified": "..."
        },
        ...
        "id": ...,
        ...
        "title": "changed Admin petition",
        ...
      }
    }


Get a Petition by id
--------------------

Use the id from the response above::

    >>> response = browser.get('/v1/admin/petitions/%s' % id)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        ...
        "dc": {
          "created": "...",
          "effective": null,
          "expires": null,
          "modified": "..."
        },
        ...
        "id": ...,
        ...
        "title": "changed Admin petition",
        ...
      }
    }


List Petitions
--------------

Use the list endpoint::

    >>> response = browser.get('/v1/admin/petitions')
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": [
        {
          ...
          "dc": {
            "created": "...",
            "effective": null,
            "expires": null,
            "modified": "..."
          },
          ...
          "id": ...,
          ...
          "title": "changed Admin petition",
          ...
        }
      ],
      "total": 1
    }


Delete a Petition
-----------------

Do a delete request::

    >>> response = browser.delete('/v1/admin/petitions/%s' % id)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        ...
        "dc": {
            "created": "...",
            "effective": null,
            "expires": null,
            "modified": "..."
        },
        ...
        "id": ...,
        ...
        "title": "changed Admin petition",
        ...
      }
    }


Search
======

Create some sampledata::

    >>> samples.petitions(30)
    >>> response = browser.get('/v1/admin/petitions')

Filter by State
---------------

Search results can be filtered by state::

    >>> response = browser.get('/v1/admin/petitions?state=draft')
    >>> print_json(response)
    {
      "data": [
        {
          ...
          "state": {
            "listable": false,
            "name": "draft",
            "parent": "",
            "timer": 0
          },
          ...
        }
      ],
      "total": 16
    }

It is possible to provide multiple states::

    >>> response = browser.get('/v1/admin/petitions?state=active,draft')
    >>> print_json(response)
    {
      "data": [
        {
          ...
        }
      ],
      "total": 25
    }

    >>> response = browser.get('/v1/admin/petitions?state=supportable.pending')
    >>> print_json(response)
    {
      ...
      "total": 5
    }
    >>> response = browser.get('/v1/admin/petitions?state=supportable.active')
    >>> print_json(response)
    {
      ...
      "total": 9
    }
    >>> response = browser.get('/v1/admin/petitions?state=supportable.*')
    >>> print_json(response)
    {
      ...
      "total": 14
    }


General Fulltext Search
-----------------------

Uses all existing fulltext fields::

    >>> response = browser.get('/v1/admin/petitions?ft=harum&sort=score')
    >>> print_json(response)
    {
      "data": [
        {
    ...
        }
      ],
      "total": 17
    }

    >>> response = browser.get('/v1/petitions?ft=Harum&sort=score')
    >>> print_json(response)
    {
      "data": [
        {
    ...
        }
      ],
      "total": 17
    }


Sorting Search Results
======================


Amount of Supporters
--------------------

Use the `supporters.amount` sort::

    >>> response = browser.get('/v1/petitions?sort=supporters.amount')
    >>> [(p['supporters']['amount'], p['id']) for p in response.json['data']]
    [(0, 22), (1, 19), (1, 10), (3, 9), (4, 5), (4, 3), (4, 15), (6, 18), (6, 8), (7, 26)]

    >>> response = browser.get('/v1/petitions?sort=-supporters.amount')
    >>> [(p['supporters']['amount'], p['id']) for p in response.json['data']]
    [(20, 11), (19, 16), (18, 28), (18, 24), (18, 7), (17, 20), (16, 6), (16, 25), (15, 14), (13, 4)]

State
-----

Use the `state` sort::

    >>> response = browser.get('/v1/petitions?sort=state&limit=5')
    >>> [(p['state']['name'], p['id']) for p in response.json['data']]
    [(u'active', 16), (u'active', 12), (u'active', 17), (u'active', 24), (u'active', 29)]

    >>> response = browser.get('/v1/petitions?sort=-state&limit=5')
    >>> [(p['state']['name'], p['id']) for p in response.json['data']]
    [(u'pending', 23), (u'pending', 18), (u'pending', 19), (u'pending', 21), (u'pending', 22)]

Combined with id sort::

    >>> response = browser.get('/v1/petitions?sort=state,id&limit=5')
    >>> [(p['state']['name'], p['id']) for p in response.json['data']]
    [(u'active', 8), (u'active', 12), (u'active', 13), (u'active', 16), (u'active', 17)]

`state.parent` sorts by parent state::

    >>> response = browser.get('/v1/petitions?sort=state.parent,id&limit=5')
    >>> [(p['state']['parent'], p['state']['name'], p['id']) for p in response.json['data']]
    [(u'', u'draft', 3), (u'', u'draft', 4), (u'', u'draft', 5), (u'', u'draft', 6), (u'', u'draft', 7)]

    >>> response = browser.get('/v1/petitions?sort=-state.parent,id&limit=5')
    >>> [(p['state']['parent'], p['state']['name'], p['id']) for p in response.json['data']]
    [(u'supportable', u'active', 8), (u'supportable', u'active', 12), (u'supportable', u'active', 13), (u'supportable', u'active', 16), (u'supportable', u'active', 17)]


Permissions
===========

Get a test city::

    >>> response = browser.get('/v1/admin/petitions')
    >>> city_id = response.json['data'][0]['id']

Permission check for all endpoints::

    >>> check_roles("GET", "/v1/admin/petitions")
    Anonymous                               deny
    Authenticated                           deny
    admin                                   200 OK
    apikey-user                             deny

    >>> check_roles("GET", "/v1/admin/petitions/%s" % city_id)
    Anonymous                               deny
    Authenticated                           deny
    admin                                   200 OK
    apikey-user                             deny

    >>> def tmp_petition():
    ...     petition = creators.petition(title='tester')
    ...     return {'petition_id': petition.id}

    >>> check_roles("DELETE", "/v1/admin/petitions/%(petition_id)s", hook=tmp_petition)
    Anonymous                               deny
    Authenticated                           deny
    admin                                   200 OK
    apikey-user                             deny
