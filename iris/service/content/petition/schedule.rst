===================
Petition Cron Tasks
===================


Tick Handling
=============

If a petition has the flag state.tick set it expects that the tick event is
called regulary.

This is done using the TickWorker::

    >>> from iris.service.content.petition.schedule import TickWorker

An instance of the TickWorker needs to be called::

    >>> worker = TickWorker()
    >>> worker()

Create a petition::

    >>> from iris.service.content.petition import Petition
    >>> p1 = creators.petition(title="petition 1")
    >>> p1_id = p1.id
    >>> p1.state, p1.state.tick
    (<StateContainer draft>, False)
    >>> worker()
    >>> p1 = Petition.get(p1_id)
    >>> p1.state, p1.state.tick
    (<StateContainer draft>, False)

Push the petition into a state which requests tick handling::

    >>> request = get_test_request()
    >>> p1.owner = {
    ...     "email": "email@iris.com",
    ...     "email_trusted": True,
    ...     "mobile": "555 1234",
    ...     "mobile_trusted": True
    ... }
    >>> _ = p1.sm(request).publish()
    >>> p1 = Petition.get(p1_id)
    >>> p1.state, p1.state.tick
    (<StateContainer supportable.pending>, False)
    >>> _ = p1.sm(request).approved()
    >>> p1.state, p1.state.tick
    (<StateContainer supportable.active>, True)
    >>> _ = p1.store(refresh=True)

Running the worker will change nothing on the petition because it is not
expired::

    >>> worker()
    >>> p1 = Petition.get(p1_id)
    >>> p1.state, p1.state.tick
    (<StateContainer supportable.active>, True)

    >>> from iris.service.db import dc
    >>> _ = dc.dc_update(p1, **{dc.DC_EXPIRES: dc.iso_now()})
    >>> _ = p1.store(refresh=True)
    >>> worker()
    >>> p1 = Petition.get(p1_id)
    >>> p1.state, p1.state.tick
    (<StateContainer loser>, False)
