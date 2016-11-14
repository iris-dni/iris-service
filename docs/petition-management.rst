===================
Petition Management
===================

.. contents::


.. _petition-management-petition-states:

Petition States
===============

A petition has a state which is controlled by the backend during it's
lifecycle. The name of the states is defined by the names in the diagram
below.

For the API requests to search for states it is also possible to provide the
name of an enclosing state. Enclosing state names always include all substates.

For information about the management of the petition state see
:ref:`petitions-manage-state`


.. uml::

    @startuml

    Title "Petition State Machine"

    [*] --> draft
    draft --> draft : edit
    draft --> supportable : [publish]

    supportable -up-> rejected : [reject]
    supportable -> deleted : [delete]

    rejected --> supportable : [publish]
    rejected : send mail to owner

    draft --> deleted : [delete]
    loser --> deleted : [delete]
    closed -> deleted : [delete]
    processing -> deleted : [delete]

    state deleted {
    }
    deleted : only marked as deleted
    deleted : not removed from database

    state loser {
    }
    note right of loser : petition is a loser because\nit didn't reached the supporter limit\nbefore the timeout

    state supportable {
      [*] --> pending
      note right of pending : supporting is active but petition\nis not in query results
      pending --> active : [approved]
      active : petition is visible to all people in all queries
      active : send approval mail to owner
      active --> loser : timeout
      active -right-> winner : supporter\nlimit reached
      
      winner : send mail to owner
      note top of winner : petition is a winner because\nit reached the supporter limit\nbefore the timeout

      winner -> processing : timeout
    }

    state processing {
        [*] --> sendLetterRequested
        sendLetterRequested : editor needs to send a letter
        sendLetterRequested --> waitForLetterResponse : [letterSent]
        waitForLetterResponse : send mail to owner
        waitForLetterResponse : enter: create response token
        waitForLetterResponse : enter: set wait expire: state.letter_wait_expire
        waitForLetterResponse --> letterResponseArrived : [setFeedback]
        waitForLetterResponse --> noLetterResponse : timeout
        noLetterResponse --> letterResponseArrived : [setFeedback]
        noLetterResponse --> closedWithoutLetterResponse : [close]
        letterResponseArrived --> closed : [close]
        letterResponseArrived : enter: delete response token
    }

    closedWithoutLetterResponse : enter: delete response token
    closedWithoutLetterResponse -> deleted : [delete]
    state closedWithoutLetterResponse {
    }
    state closed {
    }
    @enduml
