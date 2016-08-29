============================
Petition Document Management
============================


Petiton State
=============

The petition state is an instance of the StateContainer. The document provides
the state as a StateContainer instance which is used as an ObjectProperty. The
StateContainer can be JSON serialized using the jsonpickle module::

    >>> from iris.service.petition.document import StateContainer
    >>> s = StateContainer()
    >>> import jsonpickle
    >>> jsonpickle.encode(s)
    '{"py/object": "iris.service.petition.document.StateContainer", "name": "draft", "parent": ""}'
    >>> jsonpickle.encode(s, unpicklable=False)
    '{"name": "draft", "parent": ""}'

With additional properties::

    >>> s = StateContainer()
    >>> s.other = 'other'
    >>> jsonpickle.encode(s, unpicklable=False)
    '{"other": "other", "name": "draft", "parent": ""}'
    >>> jsonpickle.encode(s)
    '{"py/object": "iris.service.petition.document.StateContainer", "other": "other", "name": "draft", "parent": ""}'


Petiton Document
================

A petition is a `Document`::

    >>> from iris.service.petition.document import Petition
    >>> petition = Petition()
    >>> petition
    <Petition [id=1]>

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

Store the petition::

    >>> pp(petition.store())
    {
      "_id": "1",
      "_index": "petitions",
      "_type": "default",
      "_version": 1,
      "created": true
    }

Get the petition back from the database::

    >>> petition = Petition.get("1")
    >>> petition
    <Petition [id=1]>
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
    >>> petition = Petition.get("1")
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
    <RelationResolver User[1]>
    >>> petition.owner()
    <User [id=1, u'42@email.com']>
    >>> petition._relations
    {'images': [], 'owner': 1, 'links': [], 'videos': [], 'connected_locations': []}


Petition City
==============

The petition city is a relation to a City document::

    >>> petition = Petition()
    >>> petition.city
    <RelationResolver City[None]>
    >>> petition.city() is None
    True

    >>> city = creators.city(id='dahoam', provider="test", name='dahoam')
    >>> _ = city.store()

    >>> petition.city = city
    >>> petition.city
    <RelationResolver City[test:dahoam]>
    >>> petition.city()
    <City [id=u'test:dahoam', u'dahoam']>
    >>> petition._relations
    {'images': [], 'city': 'test:dahoam', 'links': [], 'videos': [], 'connected_locations': []}


Petition Images
===============

The petition manages a list of images as a relation list to files::

    >>> petition.images
    <ListRelationResolver File([])>


Petition Videos
===============

The petition manages a list of videos as a relation list to web locations::

    >>> petition.videos
    <ListRelationResolver WebLocation([])>


Petition Links
===============

The petition manages a list of links as a relation list to web locations::

    >>> petition.links
    <ListRelationResolver WebLocation([])>


Petition Connected Location
===========================

The petition manages a list of connected locations as a relation list to web
locations. "connected locations" are web location on which the petition is
used::

    >>> petition.connected_locations
    <ListRelationResolver WebLocation([])>


Petition Support
================

Users can support petitions::

    >>> petition = Petition()
    >>> _ = petition.store(refresh=True)
    >>> petition.supporters['required'] = 4

Support using a telephone number::

    >>> phone_user = {
    ...     "telephone": "0555 42",
    ...     "firstname": "first",
    ...     "lastname": "last",
    ... }
    >>> supporter = petition.addSupporter(phone_user=phone_user)
    >>> supporter
    <Supporter [id='2-t:0555 42']>
    >>> supporter.user() is None
    True
    >>> supporter.phone_user
    {'lastname': 'last', 'telephone': '0555 42', 'firstname': 'first'}
    >>> supporter.petition.id == petition.id
    True

    >>> from iris.service.petition.document import Supporter
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

    >>> supporter = petition.addSupporter(user=42)
    >>> supporter
    <Supporter [id='2-u:42']>
    >>> supporter.user
    <RelationResolver User[42]>
    >>> supporter.phone_user is None
    True
    >>> supporter.petition.id == petition.id
    True
    >>> petition = Petition.get(petition.id)
    >>> pp(petition.supporters)
    {
      "amount": 2,
      "required": 4
    }

Duplicate supporters are not counted::

    >>> supporter = petition.addSupporter(user=42)
    >>> supporter
    <Supporter [id=u'2-u:42']>
    >>> petition = Petition.get(petition.id)
    >>> pp(petition.supporters)
    {
      "amount": 2,
      "required": 4
    }

Supporters can be removed::

    >>> petition.removeSupporter('2-u:42')
    >>> petition = Petition.get(petition.id)
    >>> pp(petition.supporters)
    {
      "amount": 1,
      "required": 4
    }

Remove the already removed supporter again::

    >>> petition.removeSupporter('2-u:42')
    >>> petition = Petition.get(petition.id)
    >>> pp(petition.supporters)
    {
      "amount": 1,
      "required": 4
    }
