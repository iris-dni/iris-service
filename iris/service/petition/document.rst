============================
Petition Document Management
============================


Petion State
============

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


Petion Document
===============

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
