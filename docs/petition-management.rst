===================
Petition Management
===================

.. contents::


Petition States
===============

A petition can have multiple states at the same time. The state diagram below
shows the states and the transitions between the states.
A `substate` adds his internal state to the state list.

Example:

    When the state `ownerNotified` is active, the `state` property of the
    petition contains: ["supportable", "winner", "ownerNotified"]

.. uml::

    @startuml

    Title "Petition State Machine"

    [*] --> draft
    draft --> draft : edit
    draft --> supportable : publish authenticated

    supportable -up-> rejected : rejected by editor
    supportable -> deleted : deleted by editor

    rejected --> supportable : published by editor

    state rejected {
        [*] --> edit
        edit -> edit : edit
        edit --> publish_request : published by owner
    }
    rejected : send mail to owner

    state loser {
    }
    note bottom of loser : petition is a loser because\nit didn't reached the supporter limit\nbefore the timeout

    state supportable {
      [*] --> pending
      pending : send approval mail to editor
      note right of pending : supporting is active but petition\nis not in query results
      pending --> active : approved by editor
      active : petition is visible to all people in all queries
      pending --> active : auto approved\nif timeout\nand city is assigned
      active --> loser : timeout
      active -right-> winner : supporter limit reached
      
      winner : send mail to owner
      note top of winner : petition is a winner because\nit reached the supporter limit\nbefore the timeout

      winner -> processing : timeout
    }

    state processing {
        [*] --> sendLetter
        sendLetter : editor needs to send a letter
        sendLetter --> waitForLetterResponse : letter sent
        waitForLetterResponse : enter: create response token
        waitForLetterResponse : exit: delete response token
        waitForLetterResponse --> letterResponseArrived : feedback is set
        letterResponseArrived --> closed : editor switch to closed
    }

    state closed {
    }
    @enduml
