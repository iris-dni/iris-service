======================
Petition State Machine
======================

The state machine needs an instance of a petition::

    >>> from iris.service.content.petition import Petition
    >>> petition = Petition()

    >>> from iris.service.content.petition.sm import PetitionStateMachine
    >>> sm = PetitionStateMachine(petition, None)
    >>> sm.state
    'draft'
    >>> petition.state
    <StateContainer draft>

The petition can also provide the state machine::

    >>> sm = petition.sm
    >>> sm.state
    'draft'

Publish the petition::

    >>> _ = sm.publish()
    >>> sm.state
    'supportable.pending'
    >>> petition.state
    <StateContainer supportable.pending>

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
