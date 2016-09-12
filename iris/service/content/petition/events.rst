===============
Petition Events
===============

The petition event endpoints control the petition state machine.

::

    >>> import time
    >>> from iris.service.content.petition import Petition
    >>> from iris.service.content.petition.sm import APPROVAL_TIME
    >>> def showState(response):
    ...     return response.json['data']['state']

Shows the listable flag of the petition state. This flag indicates that the
petition is allowed to be seen in the public list endpoints::

    >>> def showListable(response):
    ...     return Petition.get(response.json['data']['id']).state.listable


Create And Publish Petition
===========================

User flow from creating a petition to publishing it to the supportable pending
state.

Create a new petition::

    >>> petition = {
    ...     "data": {
    ...         "title": "Create And Publish Petition"
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> id = response.json['data']['id']
    >>> showState(response)
    {u'name': u'draft', u'parent': u''}
    >>> showListable(response)
    False

Publish the petition::

    >>> response = browser.post_json('/v1/petitions/%s/event/publish' % id)
    >>> showState(response)
    {u'name': u'pending', u'parent': u'supportable'}
    >>> showListable(response)
    False


Reject a Petition
=================

Flow from creating a new petition to reject a pending petition and republish it.

Create a new petition::

    >>> petition = {
    ...     "data": {
    ...         "title": "Create And Publish Petition"
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> id = response.json['data']['id']
    >>> showState(response)
    {u'name': u'draft', u'parent': u''}
    >>> showListable(response)
    False

Publish the petition::

    >>> response = browser.post_json('/v1/petitions/%s/event/publish' % id)
    >>> showState(response)
    {u'name': u'pending', u'parent': u'supportable'}
    >>> showListable(response)
    False

Reject the petition::

    >>> body = {
    ...     "notify": False
    ... }
    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/reject' % id,
    ...     body
    ... )
    >>> showState(response)
    {u'name': u'rejected', u'parent': u''}
    >>> showListable(response)
    False

Publish the petition again::

    >>> response = browser.post_json('/v1/petitions/%s/event/publish' % id)
    >>> showState(response)
    {u'name': u'pending', u'parent': u'supportable'}
    >>> showListable(response)
    False


Activate a Petition
===================

Create a new petition::

    >>> petition = {
    ...     "data": {
    ...         "title": "Create And Publish Petition"
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> id = response.json['data']['id']

Publish the petition::

    >>> response = browser.post_json('/v1/petitions/%s/event/publish' % id)
    >>> showState(response)
    {u'name': u'pending', u'parent': u'supportable'}
    >>> showListable(response)
    False

Approve the petition::

    >>> response = browser.post_json('/v1/petitions/%s/event/approved' % id)
    >>> showState(response)
    {u'name': u'active', u'parent': u'supportable'}
    >>> showListable(response)
    True


Petition is a Winner
====================

Create a new petition::

    >>> petition = {
    ...     "data": {
    ...         "title": "Create And Publish Petition"
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> id = response.json['data']['id']
    >>> showState(response)
    {u'name': u'draft', u'parent': u''}
    >>> showListable(response)
    False

Set supporters data::

    >>> petition = Petition.get(id)
    >>> petition.supporters['amount'] = 1
    >>> petition.supporters['required'] = 10
    >>> _ = petition.store(refresh=True)

Publish the petition::

    >>> response = browser.post_json('/v1/petitions/%s/event/publish' % id)
    >>> showState(response)
    {u'name': u'pending', u'parent': u'supportable'}
    >>> showListable(response)
    False

Approve the petition::

    >>> response = browser.post_json('/v1/petitions/%s/event/approved' % id)
    >>> showState(response)
    {u'name': u'active', u'parent': u'supportable'}
    >>> showListable(response)
    True

Now the 'check' event will switch to state winner if the supporter amount is
reached::

    >>> response = browser.post_json('/v1/petitions/%s/event/check' % id)
    >>> showState(response)
    {u'name': u'active', u'parent': u'supportable'}
    >>> showListable(response)
    True

    >>> petition = Petition.get(id)
    >>> petition.supporters['amount'] = 11
    >>> _ = petition.store(refresh=True)

    >>> response = browser.post_json('/v1/petitions/%s/event/check' % id)
    >>> showState(response)
    {u'name': u'winner', u'parent': u'supportable'}
    >>> showListable(response)
    True

The winner state waits until the support time is reached. The 'tick' event
will switch after the timeout::

    >>> response = browser.post_json('/v1/petitions/%s/event/tick' % id)
    >>> showState(response)
    {u'name': u'winner', u'parent': u'supportable'}
    >>> showListable(response)
    True

    >>> petition = Petition.get(id)
    >>> petition.state.timer = int(time.time()) - APPROVAL_TIME - 1
    >>> _ = petition.store(refresh=True)

    >>> response = browser.post_json('/v1/petitions/%s/event/tick' % id)
    >>> showState(response)
    {u'name': u'sendLetterRequested', u'parent': u'processing'}
    >>> showListable(response)
    True

Go through the processing steps::

    >>> response = browser.post_json('/v1/petitions/%s/event/sendLetter' % id)
    >>> showState(response)
    {u'name': u'waitForLetterResponse', u'parent': u'processing'}
    >>> showListable(response)
    True

    >>> response = browser.post_json('/v1/petitions/%s/event/setFeedback' % id)
    >>> showState(response)
    {u'name': u'letterResponseArrived', u'parent': u'processing'}
    >>> showListable(response)
    True

    >>> response = browser.post_json('/v1/petitions/%s/event/close' % id)
    >>> showState(response)
    {u'name': u'closed', u'parent': u''}
    >>> showListable(response)
    True


Petition is a Loser
===================

Create a new petition::

    >>> petition = {
    ...     "data": {
    ...         "title": "Create And Publish Petition"
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> id = response.json['data']['id']
    >>> showState(response)
    {u'name': u'draft', u'parent': u''}
    >>> showListable(response)
    False

Set supporters data::

    >>> petition = Petition.get(id)
    >>> petition.supporters['amount'] = 1
    >>> petition.supporters['required'] = 10
    >>> _ = petition.store(refresh=True)

Publish the petition::

    >>> response = browser.post_json('/v1/petitions/%s/event/publish' % id)
    >>> showState(response)
    {u'name': u'pending', u'parent': u'supportable'}
    >>> showListable(response)
    False

Approve the petition::

    >>> response = browser.post_json('/v1/petitions/%s/event/approved' % id)
    >>> showState(response)
    {u'name': u'active', u'parent': u'supportable'}
    >>> showListable(response)
    True

Now the petition is a loser when the support timeout occures before the
supporter limit is reached::

    >>> response = browser.post_json('/v1/petitions/%s/event/tick' % id)
    >>> showState(response)
    {u'name': u'active', u'parent': u'supportable'}
    >>> showListable(response)
    True

    >>> petition = Petition.get(id)
    >>> petition.state.timer = int(time.time()) - APPROVAL_TIME - 1
    >>> _ = petition.store(refresh=True)

    >>> response = browser.post_json('/v1/petitions/%s/event/tick' % id)
    >>> showState(response)
    {u'name': u'loser', u'parent': u''}
    >>> showListable(response)
    True


Draft can be deleted
====================

Create a new petition::

    >>> petition = {
    ...     "data": {
    ...         "title": "Create And Publish Petition"
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> id = response.json['data']['id']
    >>> showState(response)
    {u'name': u'draft', u'parent': u''}
    >>> showListable(response)
    False

Delete the petition::

    >>> response = browser.post_json('/v1/petitions/%s/event/delete' % id)
    >>> showState(response)
    {u'name': u'deleted', u'parent': u''}
    >>> showListable(response)
    False


Options Requests
================

THe options request on the event endpoint is implementated as a generic
endpoint allowing to provide any event name.

An existing event name::

    >>> response = browser.options('/v1/petitions/%s/event/delete' % id)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {}

An unknown event name is also allowed::

    >>> response = browser.options('/v1/petitions/%s/event/unknown42' % id)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {}


Resolving Event Response
========================

Event response can also reolve::

    >>> city = creators.city(id='1111',
    ...                      provider='petition_events',
    ...                      name='Berlin',
    ...                      treshold=42,
    ...                     )
    >>> petition = {
    ...     "data": {
    ...         "title": "Resolve Petition",
    ...         "city": {"id": city.id}
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> id = response.json['data']['id']

    >>> response = browser.post_json('/v1/petitions/%s/event/publish?resolve=city' % id)
    >>> print_json(response)
    {
      "data": {
        "city": {
          "class": "City",
          "data": {
            "id": "petition_events:1111",
            "name": "Berlin",
            "provider": "petition_events",
            "tags": [],
            "treshold": 42,
            "zips": []
          },
          "id": "petition_events:1111"
        },
        ...
