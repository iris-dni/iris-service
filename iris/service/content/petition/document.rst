============================
Petition Document Management
============================


Petiton State
=============

The petition state is an instance of the StateContainer. The document provides
the state as a StateContainer instance which is used as an ObjectProperty. The
StateContainer can be JSON serialized using the jsonpickle module::

    >>> from iris.service.content.petition.document import StateContainer
    >>> s = StateContainer()
    >>> import jsonpickle
    >>> jsonpickle.encode(s)
    '{"py/object": "iris.service.content.petition.document.StateContainer", "name": "draft", "parent": ""}'
    >>> jsonpickle.encode(s, unpicklable=False)
    '{"name": "draft", "parent": ""}'

With additional properties::

    >>> s = StateContainer()
    >>> s.other = 'other'
    >>> jsonpickle.encode(s, unpicklable=False)
    '{"other": "other", "name": "draft", "parent": ""}'
    >>> jsonpickle.encode(s)
    '{"py/object": "iris.service.content.petition.document.StateContainer", "other": "other", "name": "draft", "parent": ""}'


Petiton Document
================

A petition is a `Document`::

    >>> from iris.service.content.petition import Petition
    >>> petition = Petition()
    >>> petition
    <Petition [id=u'1n3gf']>

Default dublin core data is set::

    >>> pp(petition.dc)
    {
      "created": "...T...+...",
      "effective": null,
      "expires": null,
      "modified": "...T...+..."
    }

The state of a petition is a state container::

    >>> petition.state
    <StateContainer draft>
    >>> petition.state.parent = 'parent'
    >>> petition.state
    <StateContainer parent.draft>
    >>> petition.state.listable
    False

Initial supporter settings::

    >>> petition.supporters
    {'amount': 0, 'required': -1}

Initial city_answer settings::

    >>> petition.city_answer
    {'text': '', 'name': ''}

Store the petition::

    >>> pp(petition.store())
    {
      "_id": "1n3gf",
      "_index": "petitions",
      "_type": "default",
      "_version": 1,
      "created": true
    }

Get the petition back from the database::

    >>> petition = Petition.get("1n3gf")
    >>> petition
    <Petition [id=u'1n3gf']>
    >>> pp(petition.dc)
    {
      "created": "...T...+...",
      "effective": null,
      "expires": null,
      "modified": "...T...+..."
    }

The state container is also restored::

    >>> petition.state
    <StateContainer parent.draft>

    >>> petition.state.other = 'other'
    >>> petition.state.other
    'other'
    >>> _ = petition.store()
    >>> petition = Petition.get("1n3gf")
    >>> petition.state.other
    u'other'


Petition Owner
==============

The petition owner is a relation to a User document::

    >>> petition = Petition()
    >>> petition.owner
    <RelationResolver User[None]>
    >>> petition.owner() is None
    True

    >>> user = creators.user(email='42@email.com')
    >>> _ = user.store()

    >>> petition.owner = user
    >>> petition.owner
    <RelationResolver User[{'town': '', 'zip': '', 'firstname': '', 'mobile_trusted': False, 'lastname': '', 'id': u'1Zbfk', 'mobile': '', 'street': '', 'email_trusted': False, 'email': ''}]>
    >>> petition.owner()
    <User [id=u'1Zbfk', u'42@email.com']>
    >>> print_json(petition._relations)
    {
      "images": [],
      "links": [],
      "mentions": [],
      "owner": {
        "email": "",
        "email_trusted": false,
        "firstname": "",
        "id": "...",
        "lastname": "",
        "mobile": "",
        "mobile_trusted": false,
        "street": "",
        "town": "",
        "zip": ""
      }
    }

The owner relation stores additional data::

    >>> petition.owner = {"street": "21 jump street"}
    >>> print_json(petition.owner.relation_dict)
    {
      "class": "User",
      "email": "",
      "email_trusted": false,
      "firstname": "",
      "id": "...",
      "lastname": "",
      "mobile": "",
      "mobile_trusted": false,
      "street": "21 jump street",
      "town": "",
      "zip": ""
    }
    >>> petition.owner = {"town": "aarau"}
    >>> print_json(petition.owner.relation_dict)
    {
      "class": "User",
      ...
      "street": "21 jump street",
      "town": "aarau",
      "zip": ""
    }


Petition City
==============

The city of a petition is a relation to a City document::

    >>> petition = Petition()
    >>> petition.city
    <RelationResolver City[None]>
    >>> petition.city() is None
    True

    >>> city = creators.city(id='dahoam',
    ...                      provider="test",
    ...                      name='dahoam',
    ...                      treshold=42,
    ...                     )
    >>> _ = city.store()

    >>> petition.city = city
    >>> petition.city
    <RelationResolver City[test:dahoam]>
    >>> petition.city()
    <City [id=u'test:dahoam', u'dahoam']>
    >>> petition._relations
    {'owner': None, 'images': [], 'city': 'test:dahoam', 'links': [], 'mentions': []}

The required supporters are update to the treshold of the city::

    >>> _ = petition.store()
    >>> petition.supporters['required']
    42


Petition Images
===============

The petition manages a list of images as a relation list to files::

    >>> petition.images
    <ListRelationResolver File([])>


Petition Links
==============

The petition manages a list of links as a relation list to web locations::

    >>> petition.links
    <ListRelationResolver WebLocation([])>

The web locations can be assigned via a url and missing locations are created
on the fly::

    >>> petition.links = [{"url": "http://www.iris.com"}]
    >>> [v() for v in petition.links]
    [<WebLocation u'http://www.iris.com'>]

    >>> petition.links = [{"id": "cd126eaf1870967a2f3d724ee935b379"},
    ...                    {"url": "http://www.iris.com/petitions"},
    ...                   ]
    >>> [v() for v in petition.links]
    [<WebLocation u'http://www.iris.com'>,
     <WebLocation u'http://www.iris.com/petitions'>]
    >>> print_json([v.relation_dict for v in petition.links])
    [
      {
        "class": "WebLocation",
        "id": "cd126eaf1870967a2f3d724ee935b379",
        "state": "visible"
      },
      {
        "class": "WebLocation",
        "id": "d965c5b9ba7363e74fb074e91af918ce",
        "state": "visible"
      }
    ]


Petition Mentions
=================

The petition manages a list of connected locations as a relation list to web
locations. "connected locations" are web location on which the petition is
used::

    >>> petition.mentions
    <ListRelationResolver WebLocation([])>

The web locations can be assigned via a url::

    >>> petition.mentions = [{"url": "http://www.iris.com"}]
    >>> [v() for v in petition.mentions]
    [<WebLocation u'http://www.iris.com'>]
    >>> print_json([v.relation_dict for v in petition.mentions])
    [
      {
        "class": "WebLocation",
        "id": "cd126eaf1870967a2f3d724ee935b379",
        "state": "visible"
      }
    ]


Petition Support
================

Users can support petitions::

    >>> request = get_test_request()
    >>> petition = Petition()
    >>> _ = petition.store(refresh=True)
    >>> petition.supporters['required'] = 4

Support using a mobile number::

    >>> data = {
    ...     "mobile": "0555 42",
    ...     "firstname": "first",
    ...     "lastname": "last",
    ... }
    >>> supporter = petition.addSupporter(request=request,
    ...                                   data=data)
    >>> supporter
    <Supporter [id=u'...-t:0555 42']>
    >>> supporter.user() is None
    True
    >>> print_json(supporter.user.relation_dict)
    {
      "class": "User",
      "email": "",
      "email_trusted": false,
      "firstname": "first",
      "id": null,
      "lastname": "last",
      "mobile": "0555 42",
      "mobile_trusted": false,
      "street": "",
      "town": "",
      "zip": ""
    }
    >>> supporter.petition.id == petition.id
    True

    >>> from iris.service.content.petition.document import Supporter
    >>> supporters = Supporter.search({"query": {"match_all": {}},})['hits']['hits']
    >>> len(supporters)
    1

    >>> petition = Petition.get(petition.id)
    >>> pp(petition.supporters)
    {
      "amount": 1,
      "required": 4
    }

Support using an existing user::

    >>> supporter = petition.addSupporter(request=request, user_id=user.id)
    >>> supporter
    <Supporter [id=u'1fjnH-u:...']>
    >>> supporter.user
    <RelationResolver User[{... 'id': u'...'}]>
    >>> print_json(supporter.user.relation_dict)
    {
      "class": "User",
      "email": "",
      "email_trusted": false,
      "firstname": "",
      "id": "...",
      "lastname": "",
      "mobile": "",
      "mobile_trusted": false,
      "street": "",
      "town": "",
      "zip": ""
    }
    >>> supporter.petition.id == petition.id
    True
    >>> petition = Petition.get(petition.id)
    >>> pp(petition.supporters)
    {
      "amount": 2,
      "required": 4
    }

Duplicate supporters are not counted::

    >>> supporter = petition.addSupporter(request=request, user_id='42')
    >>> supporter
    <Supporter [id=u'...-u:42']>
    >>> petition = Petition.get(petition.id)
    >>> pp(petition.supporters)
    {
      "amount": 3,
      "required": 4
    }

Supporters can be removed::

    >>> petition.removeSupporter(supporter.id)
    >>> petition = Petition.get(petition.id)
    >>> pp(petition.supporters)
    {
      "amount": 2,
      "required": 4
    }

Remove the already removed supporter again::

    >>> petition.removeSupporter(supporter.id)
    >>> petition = Petition.get(petition.id)
    >>> pp(petition.supporters)
    {
      "amount": 2,
      "required": 4
    }

List all supporters of a petition::

    >>> list(petition.get_supporters())
    [<Supporter [id=u'...-t:0555 42']>, <Supporter [id=u'...-u:...']>]


Check if supporting
-------------------

Check if a data set which would be used to add support can be used for a new
support::

    >>> supporter = petition.addSupporter(request=request,
    ...                                   user_id='42',
    ...                                   data={"mobile": "555 4321"}
    ...                                  )

The user is supporting::

    >>> petition.isSupporting(request, '42', {'mobile': '555 1234'})
    True

user and mobile doesn't match::

    >>> petition.isSupporting(request, '55', {'mobile': '555 1234'})
    False

The mobile number is supporting::

    >>> petition.isSupporting(request, '55', {'mobile': '555 4321'})
    True

user and mobile number is supporting::

    >>> petition.isSupporting(request, '42', {'mobile': '555 4321'})
    True
