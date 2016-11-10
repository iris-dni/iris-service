================
Petition Support
================


::

    >>> from iris.service.content.petition import Petition
    >>> from iris.service.content.petition.document import Supporter
    >>> def showInfo(response):
    ...     print response.json['data']['state']
    ...     print response.json['data']['supporters']
    >>> city = creators.city(id='4242',
    ...                      provider='petition_events',
    ...                      name='HongKong',
    ...                      treshold=42,
    ...                      location={'url':'https://www.hongkong.com'},
    ...                     )

A browser which is logged in as an administrator::

    >>> admin = get_browser()
    >>> _ = ssologin(admin, {'email': 'admin@iris.com', 'roles': ['admin']})

Create a new petition::

    >>> petition = {
    ...     "data": {
    ...         "title": "Support Petition",
    ...         "city": {"id": city.id},
    ...         "owner": {
    ...             "email": "email@iris.com",
    ...             "mobile": "555 4321"
    ...         }
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> id = response.json['data']['id']
    >>> petition = Petition.get(id)
    >>> petition.owner = {"mobile_trusted": True, "email_trusted": True}
    >>> _ = petition.store(refresh=True)

Set the supporter.required count::

    >>> petition = Petition.get(id)
    >>> petition.supporters['required'] = 6
    >>> _ = petition.store(refresh=True)

Publish the petition, initially the publishing user is supporting the
petition::

    >>> publish_body = {"data": {}}
    >>> response = browser.post_json('/v1/petitions/%s/event/publish' % id, publish_body)
    >>> showInfo(response)
    {u'letter_wait_expire': None, u'name': u'pending', u'parent': u'supportable'}
    {u'amount': 1, u'required': 6}

Support the pending petition::

    >>> _ = ssologin(browser,
    ...     {"email": "42@sso.login",
    ...      "mobile": "555 1234",
    ...      "mobile_trusted": True,
    ...     })
    >>> supporter = {
    ...     "data": {
    ...         "user": {
    ...             "email": "me@iris.com",
    ...             "mobile": "555 1234",
    ...         }
    ...     }
    ... }

With a now trusted mobile an email confirmation mail is sent because the email
is untrusted::

    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/support' % id,
    ...     supporter)
    {'message': {'global_merge_vars': [{'content': {'url': u'http://frontend/confirm/supporter/email?key=...'},
    ...
                 'to': [{'email': u'me@iris.com', 'type': 'to'}]},
     'template_content': [],
     'template_name': 'iris-supporter-mailconfirmation'}

    >>> showInfo(response)
    {u'letter_wait_expire': None, u'name': u'pending', u'parent': u'supportable'}
    {u'amount': 2, u'required': 6}

    >>> Supporter.get_by(Supporter.petition, id, size=10)
    [<Supporter [id=u'...-t:555 4321']>,
     <Supporter [id=u'...-u:...']>]

The same user supports again::

    >>> supporter = {
    ...     "data": {
    ...         "user": {
    ...             "email": "me@iris.com",
    ...             "mobile": "555 1234",
    ...         }
    ...     }
    ... }
    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/support' % id,
    ...     supporter)
    >>> showInfo(response)
    {u'letter_wait_expire': None, u'name': u'pending', u'parent': u'supportable'}
    {u'amount': 2, u'required': 6}

    >>> Supporter.get_by(Supporter.petition, id, size=10)
    [<Supporter [id=u'...-t:555 4321']>,
     <Supporter [id=u'...-u:...']>]

Support using an untrusted mobile number::

    >>> logged_in_user = ssologin(
    ...     browser,
    ...     {"email": "42-1@sso.login",
    ...      "email_trusted": True,
    ...      "mobile": "555 1234",
    ...      "mobile_trusted": True,
    ...     })
    >>> supporter = {
    ...     "data": {
    ...         "user": {
    ...             "email": "42-1@sso.login",
    ...             "mobile": '555 4242',
    ...         }
    ...     }
    ... }
    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/support' % id,
    ...     supporter)
    sendSMS(u'555 4242', 'Support', u'Your verification code is "..."')
    >>> response.json['status']
    u'error'
    >>> response.json['reasons']
    [u'mobile_untrusted']
    >>> showInfo(response)
    {u'letter_wait_expire': None, u'name': u'pending', u'parent': u'supportable'}
    {u'amount': 2, u'required': 6}

We must provide the verification token with the support request::

    >>> supporter['data']['mobile_token'] = "1sR4E"
    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/support' % id,
    ...     supporter)
    >>> obj = Supporter.get('%s-u:%s' % (response.json['data']['id'], logged_in_user.id))
    >>> print_json(obj.user.relation_dict)
    {
      "class": "User",
      "email": "42-1@sso.login",
      "email_trusted": false,
      "firstname": "",
      "id": "...",
      "lastname": "",
      "mobile": "555 4242",
      "mobile_trusted": true,
      "street": "",
      "town": "",
      "zip": ""
    }

    >>> Supporter.get_by(Supporter.petition, id, size=10)
    [<Supporter [id=u'...-t:555 4321']>,
     <Supporter [id=u'...-u:...']>,
     <Supporter [id=u'...-u:...']>]

The same mobile number again::

    >>> del supporter['data']['mobile_token']
    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/support' % id,
    ...     supporter)
    >>> showInfo(response)
    {u'letter_wait_expire': None, u'name': u'pending', u'parent': u'supportable'}
    {u'amount': 3, u'required': 6}

    >>> Supporter.get_by(Supporter.petition, id, size=10)
    [<Supporter [id=u'...-t:555 4321']>,
     <Supporter [id=u'...-u:...']>,
     <Supporter [id=u'...-u:...']>]

Approve the petition::

    >>> response = admin.post_json('/v1/petitions/%s/event/approved' % id)
    >>> showInfo(response)
    {u'letter_wait_expire': None, u'name': u'active', u'parent': u'supportable'}
    {u'amount': 3, u'required': 6}

    >>> logged_in_user = ssologin(browser,
    ...     {
    ...         "email": "142@sso.login",
    ...         "email_trusted": True,
    ...         "mobile": "555 42 0142",
    ...         "mobile_trusted": True,
    ...     }
    ... )
    >>> supporter = {
    ...     "data": {
    ...         "user": {
    ...             "email": logged_in_user.email,
    ...             "mobile": logged_in_user.mobile,
    ...         }
    ...     }
    ... }
    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/support' % id,
    ...     supporter)
    >>> showInfo(response)
    {u'letter_wait_expire': None, u'name': u'active', u'parent': u'supportable'}
    {u'amount': 4, u'required': 6}

Support until the petition is a winner::

    >>> for userId in range(200, 204):
    ...     _ = ssologin(browser,
    ...         {
    ...             "email": "%s@sso.login" % userId,
    ...             "email_trusted": True,
    ...             "mobile": '555 42 %s' % userId,
    ...             "mobile_trusted": True,
    ...         }
    ...     )
    ...     supporter = {
    ...         "data": {
    ...             "user": {
    ...                 "email": "%s@sso.login" % userId,
    ...                 "mobile": '555 42 %s' % userId,
    ...                 "firstname": 'first',
    ...                 "lastname": 'last',
    ...             }
    ...         }
    ...     }
    ...     response = browser.post_json(
    ...         '/v1/petitions/%s/event/support' % id,
    ...         supporter)
    ...     showInfo(response)
    {u'letter_wait_expire': None, u'name': u'active', u'parent': u'supportable'}
    {u'amount': 5, u'required': 6}
    {u'letter_wait_expire': None, u'name': u'winner', u'parent': u'supportable'}
    {u'amount': 6, u'required': 6}
    {u'letter_wait_expire': None, u'name': u'winner', u'parent': u'supportable'}
    {u'amount': 7, u'required': 6}
    {u'letter_wait_expire': None, u'name': u'winner', u'parent': u'supportable'}
    {u'amount': 8, u'required': 6}

Missing mobile number::

    >>> supporter = {
    ...     "data": {
    ...         "user": {
    ...             "email": "me@iris.com",
    ...         }
    ...     }
    ... }
    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/support' % id,
    ...     supporter,
    ...     expect_errors=True)
    >>> print_json(response)
    {
      "errors": {
        "code": "400",
        "description": "'mobile' is a required property...
      }
    }

Invalid mobile number::

    >>> supporter = {
    ...     "data": {
    ...         "user": {
    ...             "email": "me@iris.com",
    ...             "mobile": '555 42',
    ...         }
    ...     }
    ... }
    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/support' % id,
    ...     supporter,
    ...     expect_errors=True)
    >>> print_json(response)
    {
      "errors": {
        "code": "400",
        "description": "u'555 42' does not match...
      }
    }

Missing email::

    >>> supporter = {
    ...     "data": {
    ...         "user": {
    ...             "mobile": '555 4242',
    ...         }
    ...     }
    ... }
    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/support' % id,
    ...     supporter,
    ...     expect_errors=True)
    >>> print_json(response)
    {
      "errors": {
        "code": "400",
        "description": "'email' is a required property...
      }
    }
