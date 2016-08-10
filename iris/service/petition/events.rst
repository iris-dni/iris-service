===============
Petition Events
===============

The petition event endpoints control the petition state machine.

::

    >>> import time
    >>> from iris.service.petition import Petition
    >>> from iris.service.petition.sm import APPROVAL_TIME
    >>> def showState(response):
    ...     return response.json['data']['state']
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

    >>> response = browser.post_json('/v1/petitions/%s/event/reject' % id)
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

Now the check event will switch to state winner if the supporter amount is
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

The winner state waits until the support time is reached::

    >>> response = browser.post_json('/v1/petitions/%s/event/check' % id)
    >>> showState(response)
    {u'name': u'winner', u'parent': u'supportable'}
    >>> showListable(response)
    True

    >>> petition = Petition.get(id)
    >>> petition.state.timer = int(time.time()) - APPROVAL_TIME - 1
    >>> _ = petition.store(refresh=True)

    >>> response = browser.post_json('/v1/petitions/%s/event/check' % id)
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

    >>> response = browser.post_json('/v1/petitions/%s/event/check' % id)
    >>> showState(response)
    {u'name': u'active', u'parent': u'supportable'}
    >>> showListable(response)
    True

    >>> petition = Petition.get(id)
    >>> petition.state.timer = int(time.time()) - APPROVAL_TIME - 1
    >>> _ = petition.store(refresh=True)

    >>> response = browser.post_json('/v1/petitions/%s/event/check' % id)
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
