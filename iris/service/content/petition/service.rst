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
          "letter_wait_expire": null,
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
      "salutation": "",
      "street": "",
      "town": "",
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
      "salutation": "",
      "street": "21 jump street",
      "town": "",
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
      "salutation": "",
      "street": "21 jump street",
      "town": "",
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
      "firstname": "",
      "id": "...",
      "lastname": ""
    }


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
          "letter_wait_expire": null,
          "name": "draft",
          "parent": ""
        },
        ...
      }
    }

Resolve the session owner. This is only possible if the requesting user is the
same as the petition owner::

    >>> response = browser.get('/v1/petitions/%s?resolve=owner' % id)
    >>> print_json(response.json['data']['owner'])
    {
      "class": "User",
      "firstname": "",
      "id": "...",
      "lastname": ""
    }
    >>> _ = ssologin(browser,
    ...              {
    ...                 'email': 'writer1@iris.com',
    ...                 'firstname': 'writer1'
    ...              }
    ...             )
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
        "salutation": "",
        "state": "active"
      },
      "email": "",
      "email_trusted": false,
      "firstname": "",
      "id": "...",
      "lastname": "",
      "mobile": "",
      "mobile_trusted": false,
      "salutation": "",
      "street": "21 jump street",
      "town": "",
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
          "letter_wait_expire": null,
          "listable": false,
          "name": "draft",
          "parent": "",
          "tick": false
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
          "salutation": "",
          "street": "21 jump street",
          "town": "",
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

Resolve the location of a city::

    >>> city = creators.city(
    ...     id="100042",
    ...     provider="test",
    ...     location={"url": "https://www.aargauerzeitung.ch"},
    ...     name="aarau",
    ...     contact={
    ...         "salutation": "Good day my dear Sir",
    ...         "address": "Land of the Elves"
    ...     }
    ... )
    >>> petition = {
    ...     "data": {
    ...         "city": {"id": city.id}
    ...     }
    ... }
    >>> response = browser.post_json('/v1/admin/petitions/%s' % id,
    ...                              petition)
    >>> print_json(response)
    {
      "data": {
        "city": {
          "class": "City",
          "id": "test:100042"
        },
    ...
    >>> response = browser.post_json('/v1/admin/petitions/%s?resolve=city.location' % id,
    ...                              petition)
    >>> print_json(response)
    {
      "data": {
        "city": {
          "class": "City",
          "data": {
            "contact": {
              "address": "Land of the Elves",
              "salutation": "Good day my dear Sir"
            },
            "dc": {
                ...
            },
            "id": "test:100042",
            "location": {
              "class": "WebLocation",
              "data": {
                "dc": {
                  ...
                },
                "id": "...",
                "og": null,
                "state": "visible",
                "url": "https://www.aargauerzeitung.ch"
              },
              "id": "9badb72136e94347c3caf7a37e4f7947"
            },
            "name": "aarau",
            "portal": {},
            "provider": "test",
            "state": "active",
            "tags": [],
            "treshold": -1,
            "zips": []
          },
          "id": "test:100042"
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
            "letter_wait_expire": null,
            "listable": false,
            "name": "draft",
            "parent": "",
            "tick": false
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
    18

    >>> response = browser.get('/v1/petitions?ft=Harum&sort=score')
    >>> response.json['total']
    15


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
              "contact": {},
              "dc": {
                ...
              },
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
              ...
              "id": "...",
              ...
              "roles": [],
              "salutation": "",
              "sso": [
                {
                  "provider": "azMedien",
                  "trusted": false
                }
              ],
              "state": "disabled",
              "street": "",
              "town": "",
              "zip": ""
            },
            "email": "",
            "email_trusted": false,
            "firstname": "",
            "id": "...",
            "lastname": "",
            "mobile": "",
            "mobile_trusted": false,
            "salutation": "",
            "street": "",
            "town": "",
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
            "salutation": "",
            "street": "",
            "town": "",
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

    >>> ssologout(browser)
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

    >>> response = browser.get('/v1/petitions?sort=state.parent,state,id&limit=5')
    >>> response.json['data'][0]['state']['name']
    u'active'
    >>> response.json['data'][0]['state']['parent']
    u'supportable'

    >>> response = browser.get('/v1/petitions?sort=-state.parent,-state,id&limit=5')
    >>> response.json['data'][0]['state']['name']
    u'winner'
    >>> response.json['data'][0]['state']['parent']
    u'supportable'


Relations
=========

Images
------

The `images` property contains a list of files with an additional
`state` property.

First upload an image::

    >>> import os
    >>> import webtest
    >>> import collections
    >>> here = os.path.dirname(__file__)
    >>> img_file = open(os.path.join(here, "../../testing/blobs/iptc.jpeg"))
    >>> img_content = img_file.read()
    >>> response = browser.post('/v1/files',
    ...                         collections.OrderedDict([
    ...                             ('data', webtest.Upload('iptc.jpeg', img_content))
    ...                         ]))
    >>> image_id = response.json['data']['id']

The `state` property is stored on the relation to the locations, other public
properties are resolved::

    >>> petition = {
    ...     "data": {
    ...         "title": "petition with images",
    ...         "images": [{"id": image_id, "state": "hidden"}]
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions?resolve=images', petition)
    >>> print_json(response)
    {
      "data": {
        ...
        "images": [
          {
            "class": "File",
            "data": {
              "content_type": "image/jpeg",
              "id": "...",
              "image_proxy_base_url": "http://imageproxy/?url=/...",
              "info": {
                "height": 1,
                "width": 1
              },
              "original_url": "file:///tmp/iris-testing/uploads/..."
            },
            "id": "...",
            "state": "hidden"
          }
        ],
        ...
      }
    }


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
            "salutation": "",
            "street": "",
            "town": "",
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
            "salutation": "",
            "street": "",
            "town": "",
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


Supporters Public API
=====================

The public API is implemented via the REST mapper.


Get Supporters List
-------------------

A user can request supporters. A petition ID is required::

    >>> response = browser.get('/v1/supporters',
    ...                        expect_errors=True)
    >>> response.status
    '400 Bad Request'
    >>> print_json(response)
    {
      "errors": {
        "code": "400",
        "description": "petition is a required parameter..."
      }
    }

    >>> response = browser.get('/v1/admin/supporters?resolve=petition,user&sort=id')
    >>> petitionId = response.json['data'][0]['petition']['id']

The API is secured by a token. A petition ID is encoded within the token. If
the token is invalid, an error is returned::

    >>> response = browser.get('/v1/supporters?token=xyz&petition=' + petitionId,
    ...                        expect_errors=True)
    >>> print_json(response)
    {
      "errors": {
        "code": "403",
        "description": "Unauthorized: SupportersPublicRESTService failed permission check"
      }
    }

Correct token::

    >>> from iris.service.content.petition.security import generate_petition_token
    >>> from iris.service.content.petition.document import Petition

    >>> token = generate_petition_token(Petition.get(petitionId))

    >>> response = browser.get(
    ...     '/v1/supporters?token={t}&petition={pId}&resolve=user'.format(
    ...         t=token,
    ...         pId=petitionId,
    ...         ))
    >>> print_json(response)
    {
      "data": [
        ...
        {
          "id": "...",
          "user": {
            "firstname": "Madison",
            "id": null,
            "lastname": "Evans",
            "mobile": "+37 49 XXX XX 41",
            "mobile_trusted": false,
            "salutation": "",
            "town": "",
            "zip": ""
          }
        },
        ...
      ],
      "total": 9
    }

Admin Users do not require a token::

    >>> _ = ssologin(browser, {'email': 'tester@iris.com', 'roles': ['admin']})

    >>> response = browser.get(
    ...     '/v1/supporters?petition={pId}&resolve=user'.format(
    ...         pId=petitionId,
    ...         ))
    >>> print_json(response)
    {
      "data": [
        ...
        {
          "id": "...",
          "user": {
            "firstname": "Madison",
            "id": null,
            "lastname": "Evans",
            "mobile": "+37 49 XXX XX 41",
            "mobile_trusted": false,
            "salutation": "",
            "town": "",
            "zip": ""
          }
        },
        ...
      ],
      "total": 9
    }

But it works with a token as well::

    >>> token = generate_petition_token(Petition.get(petitionId))

    >>> response = browser.get(
    ...     '/v1/supporters?token={t}&petition={pId}&resolve=user'.format(
    ...         t=token,
    ...         pId=petitionId,
    ...         ))
    >>> print_json(response)
    {
      "data": [
        ...
        {
          "id": "...",
          "user": {
            "firstname": "Madison",
            "id": null,
            "lastname": "Evans",
            "mobile": "+37 49 XXX XX 41",
            "mobile_trusted": false,
            "salutation": "",
            "town": "",
            "zip": ""
          }
        },
        ...
      ],
      "total": 9
    }


Filter by city
--------------

Test setup::

    >>> from iris.service.content.city import City
    >>> from iris.service.content.petition import Petition

Clear all cities.portal, cities.tags, and petitions.city::

    >>> cities = City.search({"query": {"match_all":{}},
    ...                       "sort": "name", "size": 100})['hits']['hits']
    >>> for city in cities:
    ...     city.portal = {}
    ...     city.tags = []
    ...     _ = city.store()

    >>> petitions = Petition.search({"query": {"match_all":{}},
    ...                              "sort": "name", "size": 100})['hits']['hits']
    >>> for petition in petitions:
    ...     petition.city = None
    ...     _ = petition.store()

Add some test data::

    >>> cities = City.search({"query": {"match_all":{}},
    ...                       "sort": "name"})['hits']['hits']
    >>> updatedCities = []
    >>> max = 5
    >>> for i in xrange(0, max):
    ...     city = cities[i]
    ...     city.portal = {"id": "nwch:aaz2016"}
    ...     if i % 2 == 0:
    ...         city.tags = ['nwch:aaz']
    ...     else:
    ...         city.tags = ['nwch:aaz', 'nwch:blz', 'nwch:otg']
    ...     _ = city.store()
    ...     updatedCities.append(city)
    >>> city = cities[max + 1]
    >>> city.portal = {"id": "nwch:blz2016"}
    >>> _ = city.store()
    >>> updatedCities.append(city)
    >>> _ = City.refresh()

    >>> petitions = Petition.search({"query": {"match_all":{}},
    ...                              "sort": "name"})['hits']['hits']
    >>> for i in xrange(0, max):
    ...     petition = petitions[i]
    ...     city = updatedCities[i]
    ...     petition.city = city
    ...     _ = petition.store()
    >>> petition = petitions[max + 1]
    >>> petition.city = updatedCities[-1]
    >>> _ = petition.store()
    >>> _ = Petition.refresh()


Filter by city.portal::

    >>> response = browser.get('/v1/admin/petitions?city.portal.id=nwch:aaz2016')
    >>> response.json['total']
    5

    >>> response = browser.get('/v1/admin/petitions?city.portal.id=nwch:aaz2016,nwch:blz2016')
    >>> response.json['total']
    6

Filter by city.tags::

    >>> response = browser.get('/v1/admin/petitions?city.tags=nwch:aaz')
    >>> response.json['total']
    5

    >>> response = browser.get('/v1/admin/petitions?city.tags=nwch:blz')
    >>> response.json['total']
    2

    >>> response = browser.get('/v1/admin/petitions?city.tags=nwch:aaz,nwch:blz')
    >>> response.json['total']
    5

    >>> response = browser.get('/v1/admin/petitions?city.tags=nwch:otg,nwch:blz')
    >>> response.json['total']
    2


Add URL to Petition's Mentions
==============================

Create a petition::

    >>> from iris.service.content.petition import Petition
    >>> petition = Petition(title='petition')
    >>> _ = petition.store()

We need to add an API key to a request's headers::

    >>> from iris.service.security.policy import API_KEY_HEADER_NAME
    >>> headers = {
    ...     API_KEY_HEADER_NAME: 'local'
    ... }

    >>> [m() for m in petition.mentions]
    []

    >>> response = browser.get('/v1/petitions/{id}/mentions?url={url}'.format(
    ...                        id=petition.id,
    ...                        url='http://www.example.com/'),
    ...                        headers=headers)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {
      "status": "ok"
    }

    >>> petition = Petition.get(petition.id)
    >>> [m() for m in petition.mentions]
    [<WebLocation u'http://www.example.com/'>]

    >>> response = browser.get('/v1/petitions/{id}/mentions?url={url}'.format(
    ...                        id=petition.id,
    ...                        url='http://www.other-example.com/'),
    ...                        headers=headers)
    >>> response.status
    '200 OK'

    >>> petition = Petition.get(petition.id)
    >>> [m() for m in petition.mentions]
    [<WebLocation u'http://www.example.com/'>,
     <WebLocation u'http://www.other-example.com/'>]

Calling multiple times with the same URL will not add an additional entry::

    >>> response = browser.get('/v1/petitions/{id}/mentions?url={url}'.format(
    ...                        id=petition.id,
    ...                        url='http://www.other-example.com/'),
    ...                        headers=headers)
    >>> response.status
    '200 OK'

    >>> petition = Petition.get(petition.id)
    >>> [m() for m in petition.mentions]
    [<WebLocation u'http://www.example.com/'>,
     <WebLocation u'http://www.other-example.com/'>]

'Options' requests do not need an API key header::

    >>> response = browser.options('/v1/petitions/%s/mentions' % petition.id)
    >>> response.status
    '200 OK'

'Get' requests do need an API key header::

    >>> response = browser.get('/v1/petitions/{id}/mentions?url={url}'.format(
    ...                        id=petition.id,
    ...                        url='http://www.other-example.com/'),
    ...                        expect_errors=True)
    >>> response.status
    '400 Bad Request'
    >>> print_json(response)
    {
      "errors": {
        "code": "400",
        "description": "x-iris-api-key is a required parameter.\n\nFailed ..."
      }
    }

Only configured domains (see config.ini -> 'domains.automatic_mentions') are
allowed::

    >>> response = browser.get('/v1/petitions/{id}/mentions?url={url}'.format(
    ...                        id=petition.id,
    ...                        url='http://www.i-am-not-allowed.com/'),
    ...                        headers=headers,
    ...                        expect_errors=True)
    >>> response.status
    '400 Bad Request'
    >>> print_json(response)
    {
      "error": {
        "code": 400,
        "description": "Bad request: 'url' is not allowed to be automatically connected to this petition"
      }
    }

Clean up::

    >>> _ = petition.delete()
    >>> _ = Petition.refresh()

    >>> from iris.service.content.weblocation import WebLocation
    >>> _ = WebLocation.refresh()
    >>> weblocations = WebLocation.search({"query": {"match_all":{}}})
    >>> for weblocation in weblocations['hits']['hits']:
    ...     _ = weblocation.delete()
    >>> _ = WebLocation.refresh()


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

    >>> def token_hook(self, role, url, method, json_body):
    ...     petition = creators.petition(title='tester')
    ...     token = ''
    ...     if role == 'apikey-user':
    ...         token = generate_petition_token(petition)
    ...     return {
    ...         'token': token,
    ...         'petition_id': petition.id,
    ...     }
    >>> hook = {
    ...  'options': {
    ...     'pass_request_args': True,
    ...  },
    ...  'hook': token_hook
    ... }
    >>> check_roles("GET",
    ...             "/v1/supporters?petition=%(petition_id)s&token=%(token)s",
    ...             hook=hook)
    Anonymous                               deny
    Authenticated                           deny
    admin                                   deny
    apikey-user                             200 OK
    session-user                            deny
