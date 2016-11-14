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

    >>> city = creators.city(id='4242',
    ...                      provider='petition_events',
    ...                      name='HongKong',
    ...                      treshold=42,
    ...                      location={'url':'https://www.hongkong.com'},
    ...                     )
    >>> from iris.service.content.petition import Petition
    >>> p1 = creators.petition(
    ...     title="petition 1",
    ...     city=city,
    ... )
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

    >>> from iris.service import mail
    >>> mail.reset_mail_stack()
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

There is a mail::

    >>> print_json(mail.TESTING_MAIL_STACK[-1])
    {
      "message": {
        "global_merge_vars": [
          {
            "content": {
              "city": {
                "contact": {},
                "id": "petition_events:4242",
                "name": "HongKong",
                "portal": {},
                "provider": "petition_events",
                "state": "active",
                "tags": [],
                "treshold": 42,
                "zips": []
              },
              "city_answer": {
                "name": "",
                "text": ""
              },
              "dc": {
                "created": "...",
                "effective": "...",
                "expires": "...",
                "modified": "..."
              },
              "description": "",
              "id": "...",
              "images": [],
              "links": [],
              "mentions": [],
              "owner": {
                "email": "email@iris.com",
                "email_trusted": true,
                "firstname": "",
                "lastname": "",
                "mobile": "555 1234",
                "mobile_trusted": true,
                "street": "",
                "town": "",
                "zip": ""
              },
              "response_token": null,
              "state": {
                "before_loser_mail_time": "...",
                "half_time_mail_time": "...",
                "letter_wait_expire": null,
                "listable": true,
                "name": "loser",
                "parent": "",
                "tick": false
              },
              "suggested_solution": "",
              "supporters": {
                "amount": 1,
                "remaining": 41,
                "required": 42
              },
              "tags": [],
              "title": "petition 1",
              "type": ""
            },
            "name": "petition"
          }
        ],
        "merge_vars": [
          {
            "rcpt": "email@iris.com",
            "vars": [
              {
                "content": {
                  "class": "User",
                  "email": "email@iris.com",
                  "email_trusted": true,
                  "firstname": "",
                  "id": null,
                  "lastname": "",
                  "mobile": "555 1234",
                  "mobile_trusted": true,
                  "street": "",
                  "town": "",
                  "zip": ""
                },
                "name": "user"
              }
            ]
          }
        ],
        "to": [
          {
            "email": "email@iris.com",
            "type": "to"
          }
        ]
      },
      "template_content": [],
      "template_name": "iris-petition-loser-notification-for-owner"
    }
