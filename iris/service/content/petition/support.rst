================
Petition Support
================


::

    >>> from iris.service.content.petition import Petition
    >>> from iris.service.content.petition.document import Supporter
    >>> def showInfo(response):
    ...     print response.json['data']['state']
    ...     print response.json['data']['supporters']

Create a new petition::

    >>> petition = {
    ...     "data": {
    ...         "title": "Support Petition",
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

    >>> response = browser.post_json('/v1/petitions/%s/event/publish' % id)
    >>> showInfo(response)
    {u'name': u'pending', u'parent': u'supportable'}
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
    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/support' % id,
    ...     supporter)
    >>> showInfo(response)
    {u'name': u'pending', u'parent': u'supportable'}
    {u'amount': 2, u'required': 6}

    >>> Supporter.get_by(Supporter.petition, id, size=10)
    [<Supporter [id=u'1n3gf-t:555 4321']>,
     <Supporter [id=u'1n3gf-u:...']>]

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
    {u'name': u'pending', u'parent': u'supportable'}
    {u'amount': 2, u'required': 6}

    >>> Supporter.get_by(Supporter.petition, id, size=10)
    [<Supporter [id=u'1n3gf-t:555 4321']>,
     <Supporter [id=u'1n3gf-u:...']>]

Support using an untrusted mobile number::

    >>> logged_in_user = ssologin(
    ...     browser,
    ...     {"email": "42-1@sso.login",
    ...      "mobile": "555 1234",
    ...      "mobile_trusted": True,
    ...     })
    >>> supporter = {
    ...     "data": {
    ...         "user": {
    ...             "email": "42-1@sso.login",
    ...             "mobile": '0555 42',
    ...         }
    ...     }
    ... }
    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/support' % id,
    ...     supporter)
    sendSMS(u'0555 42', 'Support', u'Your verification code is "1fjnH"')
    >>> response.json['status']
    u'error'
    >>> response.json['reasons']
    [u'mobile_untrusted']
    >>> showInfo(response)
    {u'listable': False, u'parent': u'supportable', u'name': u'pending', u'timer': ...}
    {u'amount': 2, u'required': 6}

We must provide the verification token with the support request::

    >>> supporter['data']['mobile_token'] = "1fjnH"
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
      "mobile": "0555 42",
      "mobile_trusted": true,
      "street": "",
      "town": "",
      "zip": ""
    }

    >>> Supporter.get_by(Supporter.petition, id, size=10)
    [<Supporter [id=u'1n3gf-t:555 4321']>,
     <Supporter [id=u'1n3gf-u:1Zbfk']>,
     <Supporter [id=u'1n3gf-u:1QjR3']>]

The same mobile number again::

    >>> del supporter['data']['mobile_token']
    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/support' % id,
    ...     supporter)
    >>> showInfo(response)
    {u'name': u'pending', u'parent': u'supportable'}
    {u'amount': 3, u'required': 6}

    >>> Supporter.get_by(Supporter.petition, id, size=10)
    [<Supporter [id=u'1n3gf-t:555 4321']>,
     <Supporter [id=u'1n3gf-u:1Zbfk']>,
     <Supporter [id=u'1n3gf-u:1QjR3']>]

Approve the petition::

    >>> response = browser.post_json('/v1/petitions/%s/event/approved' % id)
    >>> showInfo(response)
    {u'name': u'active', u'parent': u'supportable'}
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
    {u'name': u'active', u'parent': u'supportable'}
    {u'amount': 4, u'required': 6}

Support until the petition is a winner::

    >>> for userId in range(200, 204):
    ...     _ = ssologin(browser,
    ...         {
    ...             "email": "%s@sso.login" % userId,
    ...             "email_trusted": True,
    ...             "mobile": '0555 42 %s' % userId,
    ...             "mobile_trusted": True,
    ...         }
    ...     )
    ...     supporter = {
    ...         "data": {
    ...             "user": {
    ...                 "email": "%s@sso.login" % userId,
    ...                 "mobile": '0555 42 %s' % userId,
    ...                 "firstname": 'first',
    ...                 "lastname": 'last',
    ...             }
    ...         }
    ...     }
    ...     response = browser.post_json(
    ...         '/v1/petitions/%s/event/support' % id,
    ...         supporter)
    ...     showInfo(response)
    {u'name': u'active', u'parent': u'supportable'}
    {u'amount': 5, u'required': 6}
    {u'name': u'winner', u'parent': u'supportable'}
    {u'amount': 6, u'required': 6}
    {u'name': u'winner', u'parent': u'supportable'}
    {u'amount': 7, u'required': 6}
    {u'name': u'winner', u'parent': u'supportable'}
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

Missing email::

    >>> supporter = {
    ...     "data": {
    ...         "user": {
    ...             "mobile": '0555 42',
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
