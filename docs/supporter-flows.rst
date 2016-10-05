==============
Supporter Flow
==============

.. contents::


Support Petition
================

Petition support is implemented using the `support` event: `IRIS-Swagger-UI support </swaggerui#/petition_event/support>`_

.. uml::

    @startuml
    Title Support a Petition

    actor supporter
    participant "Browser" as browser
    participant "IRIS-Service" as service
    database "Database" as db
    participant "SMS-Service" as sms

    supporter -> browser : open support screen
    supporter -> browser : fill form
    supporter -> browser : submit form
    browser -> service : POST /event/support
    service -> db : create confirmation entry
    service -> sms : send SMS to mobile number
    service -> browser : {"status": "error",\n"reason": ["mobile_untrusted"]}
    browser -> browser : show verification form
    supporter -> browser : enter code from SMS
    supporter -> browser : submit form
    browser -> service : POST /event/support with verification code
    service -> db : confirm confirmation entry
    service -> db : create support entry
    service -> browser : {status: "ok"}
    browser -> supporter : show success page

    @enduml
