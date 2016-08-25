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

    >>> samples.users(30)
    >>> samples.cities(30)
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
      "total": 9
    }

It is possible to provide multiple states::

    >>> response = browser.get('/v1/admin/petitions?state=active,draft')
    >>> response.json['total']
    15

    >>> response = browser.get('/v1/admin/petitions?state=supportable.pending')
    >>> response.json['total']
    10
    >>> response = browser.get('/v1/admin/petitions?state=supportable.active')
    >>> response.json['total']
    6
    >>> response = browser.get('/v1/admin/petitions?state=supportable.*')
    >>> response.json['total']
    21


General Fulltext Search
-----------------------

Uses all existing fulltext fields::

    >>> response = browser.get('/v1/admin/petitions?ft=harum&sort=score')
    >>> response.json['total']
    19

    >>> response = browser.get('/v1/petitions?ft=Harum&sort=score')
    >>> response.json['total']
    19


Resolve Relations
-----------------

Relations can be resolved::

    >>> response = browser.get('/v1/admin/petitions?resolve=owner,city&limit=1')
    >>> print_json(response)
    {
      "data": [
        ...
          "city": {
            "class": "City",
            "data": {
              "id": "test:...",
              "name": "New Ashley",
              "provider": "test",
              "tags": [
                "portal:gtb"
              ],
              "treshold": 10,
              "zips": [
                "30040"
              ]
            },
            "id": "test:..."
          },
          ...
          "owner": {
            "class": "User",
            "data": {
              "dc": {
                ...
              },
              "firstname": "...",
              ...
            },
            "id": ...
          },
    ...

Unresolved::

    >>> response = browser.get('/v1/admin/petitions?limit=1')
    >>> print_json(response)
    {
      "data": [
        ...
          "city": {
            "class": "City",
            "id": "test:..."
          },
          ...
          "owner": {
            "class": "User",
            "id": ...
          },
    ...


Sorting Search Results
======================


Amount of Supporters
--------------------

Use the `supporters.amount` sort::

    >>> response = browser.get('/v1/petitions?sort=supporters.amount&limit=50')
    >>> last = None
    >>> for p in response.json['data']:
    ...     amount = p['supporters']['amount']
    ...     if last is not None and last > amount:
    ...         print 'Error: amount not ascending'
    ...         break
    ...     last = amount

    >>> response = browser.get('/v1/petitions?sort=-supporters.amount')
    >>> last = None
    >>> for p in response.json['data']:
    ...     amount = p['supporters']['amount']
    ...     if last is not None and last < amount:
    ...         print 'Error: amount not descending'
    ...         break
    ...     last = amount

State
-----

Use the `state` sort::

    >>> response = browser.get('/v1/petitions?sort=state&limit=5')
    >>> response.json['data'][0]['state']['name']
    u'active'

    >>> response = browser.get('/v1/petitions?sort=-state&limit=5')
    >>> response.json['data'][0]['state']['name']
    u'winner'

`state.parent` sorts by parent state::

    >>> response = browser.get('/v1/petitions?sort=state.parent,id&limit=5')
    >>> response.json['data'][0]['state']['name']
    u'draft'
    >>> response.json['data'][0]['state']['parent']
    u''

    >>> response = browser.get('/v1/petitions?sort=-state.parent,id&limit=5')
    >>> response.json['data'][0]['state']['parent']
    u'supportable'


Supporters Admin API
====================

The admin API is implemented via the REST mapper.


Get Supporters List
-------------------

The admin can request supporters::

    >>> _ = ssologin(browser, {'email': 'tester@iris.com', 'roles': ['admin']})
    >>> response = browser.get('/v1/admin/supporters?sort=id')
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": [
        {
          "dc": {
            "created": "..."
          },
          "id": "10-t:03613949147",
          "phone_user": {
            "firstname": "Jeffrey",
            "lastname": "James",
            "telephone": "03613949147"
          },
          "user": null
        },
        ...
      ],
      "total": 180
    }


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

    >>> check_roles("GET", "/v1/admin/supporters")
    Anonymous                               deny
    Authenticated                           deny
    admin                                   200 OK
    apikey-user                             deny
