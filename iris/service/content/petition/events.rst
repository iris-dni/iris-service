===============
Petition Events
===============

The petition event endpoints control the petition state machine.

::

    >>> from iris.service import mail
    >>> import time
    >>> import dateutil
    >>> from iris.service.content.petition import Petition
    >>> from iris.service.db import dc
    >>> def showState(response):
    ...     return response.json['data']['state']

    >>> def getSupportTimers(response):
    ...     petition = Petition.get(response.json['data']['id'])
    ...     dc = petition.dc
    ...     state = petition.state
    ...     def to_py_datetime(v):
    ...         return v and dateutil.parser.parse(v)
    ...     return {
    ...         'effective': dc['effective'],
    ...         'expires': dc['expires'],
    ...         'half_time_mail_time': state.half_time_mail_time,
    ...         'before_loser_mail_time': state.before_loser_mail_time
    ...     }

Shows the listable flag of the petition state. This flag indicates that the
petition is allowed to be seen in the public list endpoints::

    >>> def showListable(response):
    ...     return Petition.get(response.json['data']['id']).state.listable

    >>> def showTick(response):
    ...     return Petition.get(response.json['data']['id']).state.tick

    >>> def support_petition(petition, count):
    ...     for i in range(count):
    ...         user = ssologin(
    ...             browser,
    ...             {
    ...                 'email': "petition-supporter-%s@iris.com" % i,
    ...                 'email_trusted': True,
    ...                 'mobile': "555123%s" % i,
    ...                 'mobile_trusted': True,
    ...             }
    ...         )
    ...         supporter = {
    ...             "data": {
    ...                 "user": {
    ...                     "email": user.email,
    ...                     "mobile": user.mobile,
    ...                 }
    ...             }
    ...         }
    ...         response = browser.post_json(
    ...             '/v1/petitions/%s/event/support' % id,
    ...             supporter)

A browser which is logged in as an administrator::

    >>> admin = get_browser()
    >>> _ = ssologin(admin, {'email': 'tester@iris.com', 'roles': ['admin']})


Create And Publish Petition
===========================

User flow from creating a petition to publishing it to the supportable pending
state.

Create a new petition::

    >>> petition = {
    ...     "data": {
    ...         "title": "Create And Publish Petition",
    ...         "owner": {
    ...             "email": "petition-owner@iris.com",
    ...             "mobile": "555 1234"
    ...         }
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> id = response.json['data']['id']
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'draft', u'parent': u''}
    >>> showListable(response)
    False
    >>> showTick(response)
    False

    >>> petition = Petition.get(id)
    >>> petition.owner = {"mobile_trusted": True, "email_trusted": True}
    >>> _ = petition.store(refresh=True)

Publish the petition::

    >>> publish_body = {"data": {}}
    >>> response = browser.post_json('/v1/petitions/%s/event/publish' % id, publish_body)
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'pending', u'parent': u'supportable'}
    >>> showListable(response)
    False
    >>> showTick(response)
    False


Reject a Petition
=================

Flow from creating a new petition to reject a pending petition and republish it.

Create a new petition::

    >>> petition = {
    ...     "data": {
    ...         "title": "Create And Publish Petition",
    ...         "owner": {
    ...             "email": "petition-owner@iris.com",
    ...             "mobile": "555 1234"
    ...         }
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> id = response.json['data']['id']
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'draft', u'parent': u''}
    >>> showListable(response)
    False

    >>> petition = Petition.get(id)
    >>> petition.owner = {"mobile_trusted": True, "email_trusted": True}
    >>> _ = petition.store(refresh=True)

Publish the petition::

    >>> response = browser.post_json('/v1/petitions/%s/event/publish' % id, publish_body)
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'pending', u'parent': u'supportable'}
    >>> showListable(response)
    False

Reject the petition::

    >>> body = {
    ...     "notify": False
    ... }
    >>> response = admin.post_json(
    ...     '/v1/petitions/%s/event/reject' % id,
    ...     body
    ... )
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'rejected', u'parent': u''}
    >>> showListable(response)
    False

A mail is triggered::

    >>> from iris.service import mail
    >>> print_json(mail.TESTING_MAIL_STACK[-1])
    {
      "message": {
    ...
      "template_name": "iris-petition-rejected"
    }

Publish the petition again::

    >>> response = browser.post_json('/v1/petitions/%s/event/publish' % id, publish_body)
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'pending', u'parent': u'supportable'}
    >>> showListable(response)
    False


Activate a Petition
===================

Create a new petition::

    >>> petition = {
    ...     "data": {
    ...         "title": "Create And Publish Petition",
    ...         "owner": {
    ...             "email": "petition-owner@iris.com",
    ...             "mobile": "555 1234"
    ...         }
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> id = response.json['data']['id']

    >>> petition = Petition.get(id)
    >>> petition.owner = {"mobile_trusted": True, "email_trusted": True}
    >>> _ = petition.store(refresh=True)

Publish the petition::

    >>> response = browser.post_json('/v1/petitions/%s/event/publish' % id, publish_body)
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'pending', u'parent': u'supportable'}
    >>> showListable(response)
    False
    >>> showTick(response)
    False
    >>> print_json(getSupportTimers(response))
    {
      "before_loser_mail_time": "...",
      "effective": "...",
      "expires": "...",
      "half_time_mail_time": "..."
    }

Approve the petition::

    >>> mail.reset_mail_stack()
    >>> response = admin.post_json('/v1/petitions/%s/event/approved' % id)
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'pending', u'parent': u'supportable'}

No mail was sent::

    >>> not mail.TESTING_MAIL_STACK
    True

The petition needs a city::

    >>> city = creators.city(id='4242',
    ...                      provider='petition_events',
    ...                      name='HongKong',
    ...                      treshold=42,
    ...                      location={'url':'https://www.hongkong.com'},
    ...                     )
    >>> petition = {
    ...     "data": {
    ...         "city": {"id": city.id}
    ...     }
    ... }
    >>> _ = browser.post_json('/v1/petitions/%s' % id, petition)
    >>> response = admin.post_json('/v1/petitions/%s/event/approved' % id)
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'active', u'parent': u'supportable'}
    >>> showListable(response)
    True
    >>> showTick(response)
    True

A mail was sent::

    >>> print_json(mail.TESTING_MAIL_STACK[-1])
    {
      "message": {
        "global_merge_vars": [
          {
    ...
        "to": [
          {
            "email": "petition-owner@iris.com",
            "type": "to"
          }
        ]
      },
      "template_content": [],
      "template_name": "iris-petition-approved"
    }


Petition is a Winner
====================

Create a new petition::

    >>> petition = {
    ...     "data": {
    ...         "title": "Create And Publish Petition",
    ...         "city": {"id": city.id},
    ...         "owner": {
    ...             "email": "petition-owner@iris.com",
    ...             "mobile": "555 1234"
    ...         }
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> id = response.json['data']['id']
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'draft', u'parent': u''}
    >>> showListable(response)
    False

    >>> petition = Petition.get(id)
    >>> petition.owner = {"mobile_trusted": True, "email_trusted": True}
    >>> _ = petition.store(refresh=True)

Set supporters data::

    >>> petition = Petition.get(id)
    >>> petition.supporters['amount'] = 1
    >>> petition.supporters['required'] = 10
    >>> _ = petition.store(refresh=True)

Publish the petition::

    >>> response = browser.post_json('/v1/petitions/%s/event/publish' % id, publish_body)
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'pending', u'parent': u'supportable'}
    >>> showListable(response)
    False

Approve the petition::

    >>> response = admin.post_json('/v1/petitions/%s/event/approved' % id)
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'active', u'parent': u'supportable'}
    >>> showListable(response)
    True
    >>> showTick(response)
    True

Now the 'check' event will switch to state winner if the supporter amount is
reached::

    >>> response = admin.post_json('/v1/petitions/%s/event/check' % id)
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'active', u'parent': u'supportable'}
    >>> showListable(response)
    True
    >>> showTick(response)
    True

Support the petition with enough supporters to be a winner::

    >>> support_petition(petition, 9)

Now the petition is in state winner::

    >>> response = admin.get('/v1/petitions/%s' % id)
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'winner', u'parent': u'supportable'}
    >>> showListable(response)
    True
    >>> showTick(response)
    True

A mail was sent to the owner of the petition::

    >>> print_json(mail.TESTING_MAIL_STACK[-1])
    {
      "message": {
        "global_merge_vars": [
          {
    ...
        "to": [
          {
            "email": "petition-owner@iris.com",
            "type": "to"
          }
        ]
      },
      "template_content": [],
      "template_name": "iris-petition-winner"
    }

The winner state waits until the support time is reached. The 'tick' event
will switch after the timeout::

    >>> mail.reset_mail_stack()
    >>> response = admin.post_json('/v1/petitions/%s/event/tick' % id)
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'winner', u'parent': u'supportable'}
    >>> showListable(response)
    True
    >>> showTick(response)
    True

    >>> petition = Petition.get(id)
    >>> _ = dc.dc_update(petition, **{dc.DC_EXPIRES: dc.time_now()})
    >>> _ = petition.store(refresh=True)

    >>> response = admin.post_json('/v1/petitions/%s/event/tick' % id)
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'sendLetterRequested', u'parent': u'processing'}
    >>> showListable(response)
    True
    >>> showTick(response)
    False

A mail for the owner::

    >>> print_json(mail.TESTING_MAIL_STACK[-2])
    {
      "message": {
        "global_merge_vars": [
          {
            "content": {
    ...
      },
      "template_content": [],
      "template_name": "iris-petition-processing-notification-for-owner"
    }

A mail for supporters::

    >>> print_json(mail.TESTING_MAIL_STACK[-1])
    {
      "message": {
        "global_merge_vars": [
          {
            "content": {
    ...
      },
      "template_content": [],
      "template_name": "iris-petition-processing-notification-for-supporters"
    }

Go through the processing steps::

    >>> mail.reset_mail_stack()
    >>> response = admin.post_json('/v1/petitions/%s/event/letterSent' % id)
    >>> showState(response)
    {u'letter_wait_expire': u'...', u'name': u'waitForLetterResponse', u'parent': u'processing'}
    >>> showListable(response)
    True

    >>> print_json(mail.TESTING_MAIL_STACK[-1])
    {
      "message": {
        "global_merge_vars": [
          {
    ...
        "to": [
          {
            "email": "petition-owner@iris.com",
            "type": "to"
          }
        ]
      },
      "template_content": [],
      "template_name": "iris-petition-letter-sent"
    }

    >>> petition = Petition.get(id)
    >>> token = petition.response_token

    >>> body = {
    ...     "data": {
    ...         "token": token,
    ...         "answer": {
    ...             "text": "machen wir gleich",
    ...             "name": "I wrote it"
    ...         }
    ...     }
    ... }
    >>> response = admin.post_json(
    ...     '/v1/petitions/%s/event/setFeedback' % id,
    ...     body
    ... )
    >>> showState(response)
    {u'letter_wait_expire': u'...', u'name': u'letterResponseArrived', u'parent': u'processing'}
    >>> showListable(response)
    True

    >>> response = admin.post_json('/v1/petitions/%s/event/close' % id)
    >>> showState(response)
    {u'letter_wait_expire': u'...', u'name': u'closed', u'parent': u''}
    >>> showListable(response)
    True

A mail was sent to the petiton owner::

    >>> print_json(mail.TESTING_MAIL_STACK[-1])
    {
      "message": {
        "global_merge_vars": [
          {
    ...
        "to": [
          {
            "email": "petition-owner@iris.com",
            "type": "to"
          }
        ]
      },
      "template_content": [],
      "template_name": "iris-petition-closed"
    }

A mail was sent to the supporters of the petition::

    >>> print_json(mail.TESTING_MAIL_STACK[-2])
    {
      "message": {
        "global_merge_vars": [
          {
            "content": {
              "city": {
    ...
        "merge_vars": [
          {
            "rcpt": "petition-supporter-0@iris.com",
            "vars": [
              {
                "content": {
                  "class": "User",
                  "email": "petition-supporter-0@iris.com",
                  "email_trusted": true,
                  "firstname": "",
                  "id": "...",
                  "lastname": "",
                  "mobile": "5551230",
                  "mobile_trusted": true,
                  "salutation": "",
                  "street": "",
                  "town": "",
                  "zip": ""
                },
                "name": "user"
              }
            ]
          },
    ...
        "to": [
          {
            "email": "petition-supporter-0@iris.com",
            "type": "to"
          },
          {
            "email": "petition-supporter-1@iris.com",
            "type": "to"
          },
          {
            "email": "petition-supporter-2@iris.com",
            "type": "to"
          },
          {
            "email": "petition-supporter-3@iris.com",
            "type": "to"
          },
          {
            "email": "petition-supporter-4@iris.com",
            "type": "to"
          },
          {
            "email": "petition-supporter-5@iris.com",
            "type": "to"
          },
          {
            "email": "petition-supporter-6@iris.com",
            "type": "to"
          },
          {
            "email": "petition-supporter-7@iris.com",
            "type": "to"
          },
          {
            "email": "petition-supporter-8@iris.com",
            "type": "to"
          }
        ]
      },
      "template_content": [],
      "template_name": "iris-petition-closed-notification-for-supporters"
    }


Petition is a Loser
===================

Create a new petition::

    >>> petition = {
    ...     "data": {
    ...         "title": "Create And Publish Petition",
    ...         "city": {"id": city.id},
    ...         "owner": {
    ...             "email": "petition-owner@iris.com",
    ...             "mobile": "555 1234"
    ...         }
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> id = response.json['data']['id']
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'draft', u'parent': u''}
    >>> showListable(response)
    False

    >>> petition = Petition.get(id)
    >>> petition.owner = {"mobile_trusted": True, "email_trusted": True}
    >>> _ = petition.store(refresh=True)

Set supporters data::

    >>> petition = Petition.get(id)
    >>> petition.supporters['amount'] = 1
    >>> petition.supporters['required'] = 10
    >>> _ = petition.store(refresh=True)

Publish the petition::

    >>> response = browser.post_json('/v1/petitions/%s/event/publish' % id, publish_body)
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'pending', u'parent': u'supportable'}
    >>> showListable(response)
    False

Approve the petition::

    >>> response = admin.post_json('/v1/petitions/%s/event/approved' % id)
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'active', u'parent': u'supportable'}
    >>> showListable(response)
    True

Support the petition so we have some mails to send::

    >>> support_petition(petition, 3)


Now the petition is a loser when the support timeout occurs before the
supporter limit is reached::

    >>> response = admin.post_json('/v1/petitions/%s/event/tick' % id)
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'active', u'parent': u'supportable'}
    >>> showListable(response)
    True

After half time is over a mail are sent to the owner::

    >>> mail.reset_mail_stack()
    >>> petition = Petition.get(id)
    >>> petition.state.half_time_mail_time = dc.iso_now()
    >>> _ = petition.store(refresh=True)
    >>> response = admin.post_json('/v1/petitions/%s/event/tick' % id)
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'active', u'parent': u'supportable'}

    >>> print_json(getSupportTimers(response))
    {
      "before_loser_mail_time": "...",
      "effective": "...",
      "expires": "...",
      "half_time_mail_time": null
    }

    >>> print_json(mail.TESTING_MAIL_STACK[-1])
    {
      "message": {
        "global_merge_vars": [
          {
            "content": {
              "city": {
    ...
      },
      "template_content": [],
      "template_name": "iris-petition-supportable-half-time"
    }

Before getting loser a mail is sent to the owner::

    >>> mail.reset_mail_stack()
    >>> petition = Petition.get(id)
    >>> petition.state.before_loser_mail_time = dc.iso_now()
    >>> _ = petition.store(refresh=True)
    >>> response = admin.post_json('/v1/petitions/%s/event/tick' % id)
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'active', u'parent': u'supportable'}

    >>> print_json(getSupportTimers(response))
    {
      "before_loser_mail_time": null,
      "effective": "...",
      "expires": "...",
      "half_time_mail_time": null
    }

    >>> print_json(mail.TESTING_MAIL_STACK[-1])
    {
      "message": {
        "global_merge_vars": [
          {
            "content": {
              "city": {
    ...
      },
      "template_content": [],
      "template_name": "iris-petition-supportable-final-spurt"
    }

Let the petition support time expire::

    >>> petition = Petition.get(id)
    >>> _ = dc.dc_update(petition, **{dc.DC_EXPIRES: dc.time_now()})
    >>> _ = petition.store(refresh=True)

    >>> response = admin.post_json('/v1/petitions/%s/event/tick' % id)
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'loser', u'parent': u''}
    >>> showListable(response)
    True

A mail for the owner::

    >>> print_json(mail.TESTING_MAIL_STACK[-2])
    {
      "message": {
        "global_merge_vars": [
          {
            "content": {
    ...
      },
      "template_content": [],
      "template_name": "iris-petition-loser-notification-for-owner"
    }

A mail for supporters::

    >>> print_json(mail.TESTING_MAIL_STACK[-1])
    {
      "message": {
        "global_merge_vars": [
          {
            "content": {
    ...
      },
      "template_content": [],
      "template_name": "iris-petition-loser-notification-for-supporters"
    }


No Letter Response
==================

Manage the timeout when waiting for a letter response::

    >>> petition = {
    ...     "data": {
    ...         "title": "No Letter Respose",
    ...         "city": {"id": city.id},
    ...         "owner": {
    ...             "email": "petition-owner@iris.com",
    ...             "mobile": "555 1234"
    ...         }
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> id = response.json['data']['id']

    >>> body = {
    ...     "to_state": "processing.waitForLetterResponse"
    ... }
    >>> response = admin.post_json(
    ...     '/v1/petitions/%s/event/force_state' % id,
    ...     body
    ... )
    >>> showState(response)
    {u'letter_wait_expire': u'...', u'name': u'waitForLetterResponse', u'parent': u'processing'}

    >>> showTick(response)
    True
    >>> response = admin.post_json('/v1/petitions/%s/event/tick' % id)
    >>> showState(response)
    {u'letter_wait_expire': u'...', u'name': u'waitForLetterResponse', u'parent': u'processing'}

    >>> petition = Petition.get(id)
    >>> petition.state.letter_wait_expire = dc.iso_now()
    >>> _ = petition.store(refresh=True)

    >>> response = admin.post_json('/v1/petitions/%s/event/tick' % id)
    >>> showState(response)
    {u'letter_wait_expire': u'...', u'name': u'noLetterResponse', u'parent': u'processing'}
    >>> showTick(response)
    False

    >>> petition = Petition.get(id)
    >>> token = petition.response_token

    >>> body = {
    ...     "data": {
    ...         "token": token,
    ...         "answer": {
    ...             "text": "machen wir gleich",
    ...             "name": "I wrote it"
    ...         }
    ...     }
    ... }
    >>> response = admin.post_json(
    ...     '/v1/petitions/%s/event/setFeedback' % id,
    ...     body
    ... )
    >>> showState(response)
    {u'letter_wait_expire': u'...', u'name': u'letterResponseArrived', u'parent': u'processing'}

Close without letter response::

    >>> body = {
    ...     "to_state": "processing.waitForLetterResponse"
    ... }
    >>> response = admin.post_json(
    ...     '/v1/petitions/%s/event/force_state' % id,
    ...     body
    ... )
    >>> showState(response)
    {u'letter_wait_expire': u'...', u'name': u'waitForLetterResponse', u'parent': u'processing'}
    >>> petition = Petition.get(id)
    >>> petition.state.letter_wait_expire = dc.iso_now()
    >>> petition.owner = {'email_trusted': True}
    >>> _ = petition.store(refresh=True)
    >>> response = admin.post_json('/v1/petitions/%s/event/tick' % id)
    >>> showState(response)
    {u'letter_wait_expire': u'...', u'name': u'noLetterResponse', u'parent': u'processing'}

    >>> mail.reset_mail_stack()
    >>> response = admin.post_json('/v1/petitions/%s/event/close' % id)
    >>> showState(response)
    {u'letter_wait_expire': u'...', u'name': u'closedWithoutLetterResponse', u'parent': u''}

    >>> print_json(mail.TESTING_MAIL_STACK[-1])
    {
      "message": {
        "global_merge_vars": [
          {
            "content": {
              "city": {
    ...
      "template_content": [],
      "template_name": "iris-petition-closed-without-response"
    }


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
    {u'letter_wait_expire': None, u'name': u'draft', u'parent': u''}
    >>> showListable(response)
    False

Delete the petition::

    >>> response = admin.post_json('/v1/petitions/%s/event/delete' % id)
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'deleted', u'parent': u''}
    >>> showListable(response)
    False


Options Requests
================

The options request on the event endpoint is implemented as a generic endpoint
allowing to provide any event name.

An existing event name::

    >>> response = browser.options('/v1/petitions/%s/event/delete' % id)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {}

An unknown event name is also allowed::

    >>> response = browser.options('/v1/petitions/%s/event/unknown42' % id)
    >>> response.status
    '200 OK'
    >>> print_json(response)
    {}


Resolving Event Response
========================

Event response can also reolve::

    >>> city = creators.city(id='1111',
    ...                      provider='petition_events',
    ...                      name='Berlin',
    ...                      treshold=42,
    ...                      location={'url':'https://www.aargauerzeitung.ch'},
    ...                     )
    >>> petition = {
    ...     "data": {
    ...         "title": "Resolve Petition",
    ...         "city": {"id": city.id},
    ...         "owner": {
    ...             "email": "petition-owner@iris.com",
    ...             "mobile": "555 1234"
    ...         }
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> id = response.json['data']['id']

    >>> petition = Petition.get(id)
    >>> petition.owner = {"mobile_trusted": True, "email_trusted": True}
    >>> _ = petition.store(refresh=True)

    >>> response = browser.post_json('/v1/petitions/%s/event/publish?resolve=city' % id, publish_body)
    >>> print_json(response)
    {
      "data": {
        "city": {
          "class": "City",
          "data": {
            "id": "petition_events:1111",
              "location": {
                "class": "WebLocation",
                "id": "9badb72136e94347c3caf7a37e4f7947"
              },
              "name": "Berlin",
              "portal": {},
            "provider": "petition_events",
            "tags": [],
            "treshold": 42,
            "zips": []
          },
          "id": "petition_events:1111"
        },
        ...

Extending The Event Response
============================

Event response data can also be extended::

    >>> petition = {
    ...     "data": {
    ...         "title": "Extend Petition",
    ...         "owner": {
    ...             "email": "petition-owner@iris.com",
    ...             "mobile": "555 1234"
    ...         }
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> id = response.json['data']['id']

    >>> petition = Petition.get(id)
    >>> petition.owner = {"mobile_trusted": True, "email_trusted": True}
    >>> _ = petition.store(refresh=True)

    >>> response = browser.post_json('/v1/petitions/%s/event/publish?extend=supporting' % id, publish_body)
    >>> print_json(response)
    {
        ...
        "extensions": {
          "supporting": true
        },
        ...


Force A State
=============

It is possible to force the state machine into any state::

    >>> body = {
    ...     "to_state": "closed"
    ... }
    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/force_state' % id,
    ...     body,
    ...     expect_errors=True
    ... )
    >>> response.status
    '403 Forbidden'
    >>> print_json(response)
    {
      "errors": {
        "code": "403",
        "description": "Unauthorized: PetitionPublicRESTService failed permission check"
      }
    }

The user must have the 'admin' role::

    >>> response = admin.post_json(
    ...     '/v1/petitions/%s/event/force_state' % id,
    ...     body
    ... )
    >>> print_json(response)
    {
      "data": {
        ...
        "id": "...",
        ...
        "state": {
          "letter_wait_expire": null,
          "name": "closed",
          "parent": ""
        },
        ...
      },
      "status": "ok"
    }
    >>> showState(response)
    {u'letter_wait_expire': None, u'name': u'closed', u'parent': u''}
