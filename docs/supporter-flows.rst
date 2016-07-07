===============
Supperter Flows
===============

.. contents::


Supporter Signs Petition
========================

This diagram shows how the frontend needs to use the service to enable a
supporter to support a petition.

.. uml::

    @startuml
    Title Supporter Signs Petition

    actor supporter
    participant "Browser" as browser
    participant "IRIS-Service" as service
    database "Database" as db

    supporter -> browser : opens petition page
    supporter -> browser : clicks sign

    alt not authenticated
      browser -> supporter : select auth type (mobile/sso)
    else not trusted
      browser -> supporter : trust via sso
    end

    browser -> service : /petition/<id>/sign
    alt status == OK
        service -> db : store signature for petition
        service -> browser : status "OK"
        browser -> supporter : thank you
    else status == alreadySigned
        service -> browser : status "alreadySigned"
        browser -> supporter : duplicate signature
    end

    @enduml
