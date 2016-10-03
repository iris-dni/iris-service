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
    ...             "mobile": "555 1234"
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

    >>> _ = ssologin(browser, {"email": "42@sso.login"})
    >>> supporter = {"data": {}}
    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/support' % id,
    ...     supporter)
    >>> showInfo(response)
    {u'name': u'pending', u'parent': u'supportable'}
    {u'amount': 2, u'required': 6}

    >>> Supporter.get_by(Supporter.petition, id, size=10)
    [<Supporter [id=u'1n3gf-u:iris-session:...']>,
     <Supporter [id=u'1n3gf-u:...']>]

The same user supports again::

    >>> supporter = {"data": {}}
    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/support' % id,
    ...     supporter)
    >>> showInfo(response)
    {u'name': u'pending', u'parent': u'supportable'}
    {u'amount': 2, u'required': 6}

    >>> Supporter.get_by(Supporter.petition, id, size=10)
    [<Supporter [id=u'1n3gf-u:iris-session:...']>,
     <Supporter [id=u'1n3gf-u:1Zbfk']>]

Support using a telephone number::

    >>> _ = ssologout(browser)
    >>> supporter = {
    ...     "data": {
    ...         "phone_user": {
    ...             "telephone": '0555 42',
    ...             "firstname": 'first',
    ...             "lastname": 'last',
    ...         }
    ...     }
    ... }
    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/support' % id,
    ...     supporter)
    >>> showInfo(response)
    {u'name': u'pending', u'parent': u'supportable'}
    {u'amount': 3, u'required': 6}

    >>> obj = Supporter.get('1n3gf-t:0555 42')
    >>> obj.user
    <RelationResolver User[None]>
    >>> obj.phone_user
    {u'lastname': u'last', u'telephone': u'0555 42', u'firstname': u'first'}

    >>> Supporter.get_by(Supporter.petition, id, size=10)
    [<Supporter [id=u'1n3gf-u:iris-session:...']>,
     <Supporter [id=u'1n3gf-u:1Zbfk']>,
     <Supporter [id=u'1n3gf-t:0555 42']>]

The same telephone number again::

    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/support' % id,
    ...     supporter)
    >>> showInfo(response)
    {u'name': u'pending', u'parent': u'supportable'}
    {u'amount': 3, u'required': 6}

    >>> Supporter.get_by(Supporter.petition, id, size=10)
    [<Supporter [id=u'1n3gf-u:iris-session:...']>,
     <Supporter [id=u'1n3gf-u:1Zbfk']>,
     <Supporter [id=u'1n3gf-t:0555 42']>]

Approve the petition::

    >>> response = browser.post_json('/v1/petitions/%s/event/approved' % id)
    >>> showInfo(response)
    {u'name': u'active', u'parent': u'supportable'}
    {u'amount': 3, u'required': 6}

    >>> _ = ssologin(browser, {"email": "142@sso.login"})
    >>> supporter = {"data": {}}
    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/support' % id,
    ...     supporter)
    >>> showInfo(response)
    {u'name': u'active', u'parent': u'supportable'}
    {u'amount': 4, u'required': 6}

Support until the petition is a winner::

    >>> for userId in range(200, 204):
    ...     supporter = {"data": {}}
    ...     _ = ssologin(browser, {"email": "%s@sso.login" % userId})
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

Invalid phone_user data::

    >>> supporter = {
    ...     "data": {
    ...         "phone_user": {
    ...             "firstname": 'first',
    ...             "lastname": 'last',
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
        "description": "'telephone' is a required property...
      }
    }
