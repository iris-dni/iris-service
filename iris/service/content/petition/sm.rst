======================
Petition State Machine
======================

    >>> request = get_test_request()
    >>> user = creators.user(email="me@iris.com")
    >>> request.user = user

The state machine needs an instance of a petition::

    >>> from iris.service.content.petition import Petition
    >>> petition = Petition()
    >>> pprint(petition.dc)
    {'created': '...+00:00',
     'effective': None,
     'expires': None,
     'modified': '...+00:00'}

The initial state::

    >>> from iris.service.content.petition.sm import PetitionStateMachine
    >>> sm = PetitionStateMachine(petition, request)
    >>> sm.state
    'draft'
    >>> petition.state
    <StateContainer draft>


Publish the petition
====================

Transition to publish::

    >>> _ = sm.publish()
    Traceback (most recent call last):
    ConditionError: 400
    >>> sm.state
    'draft'
    >>> pprint(petition.dc)
    {'created': '...+00:00',
     'effective': None,
     'expires': None,
     'modified': '...+00:00'}

The petition must be in a publishable state::

    >>> petition.owner = {
    ...     "email": "email@iris.com",
    ...     "email_trusted": True,
    ...     "mobile": "555 1234",
    ...     "mobile_trusted": True
    ... }

    >>> _ = sm.publish()
    >>> sm.state
    'supportable.pending'
    >>> petition.state
    <StateContainer supportable.pending>
    >>> pprint(petition.dc)
    {'created': '...+00:00',
     'effective': datetime.datetime(..., tzinfo=<UTC>),
     'expires': datetime.datetime(..., tzinfo=<UTC>),
     'modified': '...+00:00'}

A new instance of the petition state machine initializes with the current
state of the petition::

    >>> sm = PetitionStateMachine(petition, None)
    >>> sm.state
    'supportable.pending'
    >>> petition.state
    <StateContainer supportable.pending>

    >>> _ = sm.approved()
    >>> sm.state
    'supportable.active'


Force A State
=============

This is an addition to make it easy to test a petition by being able to force
the statemachine into any state::

    >>> petition = Petition()
    >>> sm = PetitionStateMachine(petition, None)
    >>> sm.force_state('closed')
    True
    >>> sm.state
    'closed'

Enter and Exit code is also executed::

    >>> petition.state.listable
    False
    >>> sm.force_state('processing.sendLetterRequested')
    True
    >>> sm.state
    'processing.sendLetterRequested'
    >>> petition.state.listable
    True
    >>> petition.state.timer
    0
    >>> sm.force_state('supportable.pending')
    True
    >>> sm.state
    'supportable.pending'
