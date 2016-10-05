=================
Petition Services
=================


Public API
==========

The public API contains the endpoints which are available for the frontend.


Create Petition
---------------

Create a new petition as an unauthenticated user::

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

The owner is a session user because the browser was not logged in::

    >>> print_json(response.json['data']['owner'])
    {
      "class": "User",
      "email": "",
      "email_trusted": false,
      "firstname": "",
      "id": "iris-session:...",
      "lastname": "",
      "mobile": "",
      "mobile_trusted": false,
      "street": "",
      "zip": ""
    }

    >>> id = response.json['data']['id']

The required supporter amount is set to -1 because no city was provided::

    >>> print_json(response.json['data']['supporters'])
    {
      "amount": 0,
      "required": -1
    }


Update Petition
---------------

Update a petition::

    >>> city = creators.city(id='1111',
    ...                      provider='petition_events',
    ...                      name='Berlin',
    ...                      treshold=42,
    ...                     )
    >>> petition = {
    ...     "data": {
    ...         "title": "updated title",
    ...         "city": {"id": city.id},
    ...         "owner": {"street": "21 jump street"},
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions/%s' % id, petition)

    >>> print_json(response.json['data']['city'])
    {
      "class": "City",
      "id": "petition_events:1111"
    }

    >>> print_json(response.json['data']['owner'])
    {
      "class": "User",
      "email": "",
      "email_trusted": false,
      "firstname": "",
      "id": "iris-session:...",
      "lastname": "",
      "mobile": "",
      "mobile_trusted": false,
      "street": "21 jump street",
      "zip": ""
    }

The required amount of supporters is updated to the treshold of the city::

    >>> print_json(response.json['data']['supporters'])
    {
      "amount": 0,
      "required": 42
    }

Resetting the city::

    >>> petition = {
    ...     "data": {
    ...         "city": {
    ...             "id": None,
    ...             "class": None,
    ...             "data": None,
    ...         },
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions/%s' % id, petition)

    >>> print_json(response.json['data']['city'])
    {
      "class": "City",
      "id": null
    }

The owner id can be changed from a session user to a "real" user by logging in
and updating the petition::

    >>> _ = ssologin(browser,
    ...              {
    ...                 'email': 'writer1@iris.com',
    ...                 'firstname': 'writer1'
    ...              }
    ...             )
    >>> petition = {
    ...     "data": {
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions/%s?resolve=owner' % id, petition)
    >>> print_json(response.json['data']['owner'])
    {
      "class": "User",
      "data": {
        ...
        "firstname": "writer1",
        ...
      },
      "email": "",
      "email_trusted": false,
      "firstname": "",
      "id": "1Zbfk",
      "lastname": "",
      "mobile": "",
      "mobile_trusted": false,
      "street": "21 jump street",
      "zip": ""
    }

This is only possible if the previous owner was a session user::

    >>> _ = ssologin(browser,
    ...              {
    ...                 'email': 'writer2@iris.com',
    ...                 'firstname': 'writer2'
    ...              }
    ...             )
    >>> response = browser.post_json('/v1/petitions/%s?resolve=owner' % id, petition)
    >>> print_json(response.json['data']['owner'])
    {
      "class": "User",
      "data": {
        ...
        "firstname": "writer1",
        ...
      },
    ...


Get Petition
------------

Get a petition back using the petition id::

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

Resolve the session owner::

    >>> response = browser.get('/v1/petitions/%s?resolve=owner' % id)
    >>> print_json(response.json['data']['owner'])
    {
      "class": "User",
      "data": {
        "dc": {
          "created": "...",
          "modified": "..."
        },
        "firstname": "writer1",
        "id": "...",
        "lastname": "",
        "state": "active"
      },
      "email": "",
      "email_trusted": false,
      "firstname": "",
      "id": "...",
      "lastname": "",
      "mobile": "",
      "mobile_trusted": false,
      "street": "21 jump street",
      "zip": ""
    }


Delete Petition
---------------

Delete a petition using the petition id::

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
    ...         "title": "changed Admin petition",
    ...         "owner": {
    ...             "street": "21 jump street"
    ...         },
    ...     }
    ... }
    >>> response = browser.post_json('/v1/admin/petitions/%s' % id,
    ...                              petition)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "data": {
        "city": {
          "class": "City",
          "id": null
        },
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
        "owner": {
          "class": "User",
          "email": "",
          "email_trusted": false,
          "firstname": "",
          "id": "...",
          "lastname": "",
          "mobile": "",
          "mobile_trusted": false,
          "street": "21 jump street",
          "zip": ""
        },
        ...
        "title": "changed Admin petition",
        ...
      }
    }

Update the city relation::

    >>> petition = {
    ...     "data": {
    ...         "city": {"id": 'test:42'}
    ...     }
    ... }
    >>> response = browser.post_json('/v1/admin/petitions/%s' % id,
    ...                              petition)
    >>> print_json(response)
    {
      "data": {
        "city": {
          "class": "City",
          "id": "test:42"
        },
    ...

    >>> response = browser.post_json('/v1/admin/petitions/%s?resolve=city,owner' % id,
    ...                              petition)
    >>> print_json(response)
    {
      "data": {
        "city": {
          "class": "City",
          "data": null,
          "id": "test:42"
        },
    ...


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

    >>> response = browser.get('/v1/admin/petitions/%s,unknown' % id)
    >>> print_json(response)
    {
      "items": [
        {
          ...
          "id": "...",
          ...
        },
        null
      ]
    }
    >>> len(response.json['items'])
    2
    >>> 'data' in response.json
    False

    >>> response = browser.get('/v1/admin/petitions/%s,' % id)
    >>> print_json(response)
    {
      "items": [
        {
          ...
          "id": "...",
          ...
        }
      ]
    }
    >>> len(response.json['items'])
    1
    >>> 'data' in response.json
    False


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
              ...
              "provider": "test",
              ...
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
              "email": "...",
              ...
              "firstname": "...",
              ...
            },
            "email": "",
            "email_trusted": false,
            "firstname": "",
            "id": "...",
            "lastname": "",
            "mobile": "",
            "mobile_trusted": false,
            "street": "",
            "zip": ""
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
            "email": "",
            "email_trusted": false,
            "firstname": "",
            "id": "...",
            "lastname": "",
            "mobile": "",
            "mobile_trusted": false,
            "street": "",
            "zip": ""
          },
    ...


Extend Petitions
================

supporting
----------

Extends the petitions with the `supporting` flag which is set to true if the
currently logged in user is supporting the petition.

Create a petition::

    >>> request = get_test_request()
    >>> petition = creators.petition(title="supported")
    >>> user = creators.user(email="me@home.com")
    >>> supporter = petition.addSupporter(request=request, user_id=user.id)
    >>> response = browser.get('/v1/petitions/%s' % petition.id)
    >>> 'extensions' in response.json['data']
    False

With a user not supporting the petition::

    >>> response = browser.get('/v1/petitions/%s?extend=supporting' % petition.id)
    >>> print_json(response.json['data']['extensions'])
    {
      "supporting": false
    }

With a user supporting the petition::

    >>> _ = ssologin(browser, {'email': 'me@home.com'})
    >>> response = browser.get('/v1/petitions/%s?extend=supporting' % petition.id)
    >>> print_json(response.json['data']['extensions'])
    {
      "supporting": true
    }

Query results can also be extended::

    >>> response = browser.get('/v1/petitions?extend=supporting')
    >>> print_json(response.json['data'][0]['extensions'])
    {
      "supporting": false
    }

Clean up::

    >>> _ = petition.removeSupporter(supporter.id)
    >>> _ = petition.delete(refresh=True)
    >>> _ = user.delete(refresh=True)


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


Relations
=========

Links
-----

The `links` property contains a list of WebLocations with an additional
`state` property. The `state` property is stored on the relation to the
locations::

    >>> petition = {
    ...     "data": {
    ...         "title": "petition with links",
    ...         "images": [{"id": "42", "state": "hidden"}],
    ...         "links": [{"id": "1", "state": "hidden"},
    ...                   {"url": "http://www.iris.com",
    ...                    "data": {"url": "http://www.iris.com"}
    ...                   }],
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions?resolve=links', petition)
    >>> print_json(response)
    {
      "data": {
        ...
        "images": [
          {
            "class": "File",
            "id": "42",
            "state": "hidden"
          }
        ],
        "links": [
          {
            "class": "WebLocation",
            "data": null,
            "id": "1",
            "state": "hidden"
          },
          {
            "class": "WebLocation",
            "data": {
              "dc": {
                "created": "...",
                "modified": "..."
              },
              "id": "cd126eaf1870967a2f3d724ee935b379",
              "og": null,
              "state": "visible",
              "url": "http://www.iris.com"
            },
            "id": "cd126eaf1870967a2f3d724ee935b379",
            "state": "visible"
          }
        ],
        ...
      }
    }
    >>> r_data = response.json['data']
    >>> id = r_data["id"]

Change links::

    >>> petition = {
    ...     "data": {
    ...         "links": [r_data['links'][0],
    ...                   r_data['links'][1],
    ...                   {"url": "http://www.lovelysystems.com",
    ...                    "data": {"url": "http://lovelysystems.com"},
    ...                   }],
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions/%s?resolve=links' % id, petition)
    >>> print_json(response)
    {
      "data": {
        ...
        "images": [
          {
            "class": "File",
            "id": "42",
            "state": "hidden"
          }
        ],
        "links": [
          {
            "class": "WebLocation",
            "data": null,
            "id": "1",
            "state": "hidden"
          },
          {
            "class": "WebLocation",
            "data": {
              "dc": {
                "created": "...",
                "modified": "..."
              },
              "id": "cd126eaf1870967a2f3d724ee935b379",
              "og": null,
              "state": "visible",
              "url": "http://www.iris.com"
            },
            "id": "cd126eaf1870967a2f3d724ee935b379",
            "state": "visible"
          },
          {
            "class": "WebLocation",
            "data": {
              ...
              "id": "7475a93ef23212288d3735f17847b32a",
              "og": null,
              "state": "visible",
              "url": "http://www.lovelysystems.com"
            },
            "id": "7475a93ef23212288d3735f17847b32a",
            "state": "visible"
          }
        ],
        ...
      }
    }


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
          "id": "...",
          "petition": {
            "class": "Petition",
            "id": "..."
          },
          "user": {
            "class": "User",
            "email": "",
            "email_trusted": false,
            "firstname": "...",
            "id": null,
            "lastname": "...",
            "mobile": "...",
            "mobile_trusted": false,
            "street": "",
            "zip": ""
          }
        },
        ...
      ],
      "total": 183
    }

    >>> response = browser.get('/v1/admin/supporters?resolve=petition,user&sort=id')
    >>> print_json(response)
    {
      "data": [
        {
          "dc": {
            "created": "..."
          },
          "id": "...",
          "petition": {
            "class": "Petition",
            "data": {
              "city": {
                "class": "City",
                "id": "test:..."
              },
          ...
          "user": {
            "class": "User",
            "data": null,
            "email": "",
            "email_trusted": false,
            "firstname": "...",
            "id": null,
            "lastname": "...",
            "mobile": "...",
            "mobile_trusted": false,
            "street": "",
            "zip": ""
          }
    ...


Create Petition with invalid mobile number::

    >>> petition = {
    ...     "data": {
    ...         "title": "Public petition",
    ...         "owner": {
    ...             "mobile": "555 42"
    ...         }
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition, expect_errors=True)
    >>> response.status
    '400 Bad Request'
    >>> print_json(response)
    {
      "errors": {
        "code": "400",
        "description": "u'555 42' does not match..."
      }
    }

    >>> response = browser.post_json('/v1/admin/petitions', petition, expect_errors=True)
    >>> response.status
    '400 Bad Request'
    >>> print_json(response)
    {
      "errors": {
        "code": "400",
        "description": "u'555 42' does not match..."
      }
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
    session-user                            deny

    >>> check_roles("GET", "/v1/admin/petitions/%s" % city_id)
    Anonymous                               deny
    Authenticated                           deny
    admin                                   200 OK
    apikey-user                             deny
    session-user                            deny

    >>> def tmp_petition():
    ...     petition = creators.petition(title='tester')
    ...     return {'petition_id': petition.id}

    >>> check_roles("DELETE", "/v1/admin/petitions/%(petition_id)s", hook=tmp_petition)
    Anonymous                               deny
    Authenticated                           deny
    admin                                   200 OK
    apikey-user                             deny
    session-user                            deny

    >>> check_roles("GET", "/v1/admin/supporters")
    Anonymous                               deny
    Authenticated                           deny
    admin                                   200 OK
    apikey-user                             deny
    session-user                            deny
