================
Petitioner Flows
================

.. contents::


Petitioner Creates a Petition
=============================

This diagram shows how the frontend needs to use the service to enable a
petitioner to create and edit a petition.

.. uml::

    @startuml
    Title Create a Petition

    actor petitioner
    participant "Browser" as browser
    participant "IRIS-Service" as service
    database "Database" as db

    == Creation ==

    petitioner -> browser : open petition form
    petitioner -> browser : fill form
    petitioner -> browser : submit form
    browser -> service : POST /petition
    service -> db : store petition as draft

    alt sso authenticated
      service -> browser : status == "ok"
      note right
        - petition has been stored
        - user is assigned to the petition
        - submit is possible
      end note
    else not authenticated
      service -> browser : status == "unauthenticated"
      note right
        - petition has been stored
        - user must authenticate
        - submit is not possible
      end note
    else authenticated but not trusted
      service -> browser : status == "untrusted"
      note right
        - petition has been stored
        - user is assigned to the petition
        - user must convert to a trusted user (SSO or mobile)
        - submit is not possible
      end note
    end

    == Preview / Edit ==

    loop until submitted with status == "ok"
      browser -> petitioner : show editable preview
      note right
        depending on the returned status above the user must be
        informed about it's status on the petition.
      end note
      petitioner -> browser : submit petition
      
      browser -> service : POST /petition/<id>/submit
      
      alt sso authenticated
        service -> db : change petition status to signable
        service -> browser : status == "ok"
        note right
          - petition is now activated
          - edit is no longer possible
        end note
      else not authenticated
        service -> browser : status == "unauthenticated"
        note right
          - petition is not changed
          - user must authenticate
        end note
      else authenticated but not trusted
        service -> browser : status == "untrusted"
        note right
          - petition is not changed
          - user must convert to a trusted user (SSO or mobile)
        end note
      end
    end

    == Submitted ==

    browser -> petitioner : show petition page

    @enduml


Petitioner Edits His Rejected Petition
======================================

This diagram shows how the frontend needs to use the service to enable a
petition owner to edit his rejected petition.

.. uml::

    @startuml
    Title Edit a Rejected Petition

    actor petitioner
    participant "Browser" as browser
    participant "IRIS-Service" as service
    database "Database" as db

    loop until submitted with status == "ok"
      browser -> petitioner : show editable preview
      petitioner -> browser : submit petition
      
      browser -> service : POST /petition/<id>/submit
      
      alt sso authenticated
        service -> db : change petition status to publish_request
        service -> browser : status == "ok"
        note right
          - petition is now activated
          - edit is no longer possible
        end note
      else not authenticated
        service -> browser : status == "unauthenticated"
        note right
          - petition is not changed
          - user must authenticate
        end note
      else authenticated but not trusted
        service -> browser : status == "untrusted"
        note right
          - petition is not changed
          - user must convert to a trusted user (SSO or mobile)
        end note
      end
    end

    @enduml
