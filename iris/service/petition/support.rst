================
Petition Support
================


::

    >>> from iris.service.petition import Petition
    >>> from iris.service.petition.document import Supporter
    >>> def showInfo(response):
    ...     print response.json['data']['state']
    ...     print response.json['data']['supporters']

Create a new petition::

    >>> petition = {
    ...     "data": {
    ...         "title": "Support Petition"
    ...     }
    ... }
    >>> response = browser.post_json('/v1/petitions', petition)
    >>> id = response.json['data']['id']

Set the supporter.required count::

    >>> petition = Petition.get(id)
    >>> petition.supporters['required'] = 5
    >>> _ = petition.store(refresh=True)

Publish the petition::

    >>> response = browser.post_json('/v1/petitions/%s/event/publish' % id)
    >>> showInfo(response)
    {u'name': u'pending', u'parent': u'supportable'}
    {u'amount': 0, u'required': 5}

Support the pending petition::

    >>> supporter = {"data": {"user": 42}}
    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/support' % id,
    ...     supporter)
    >>> showInfo(response)
    {u'name': u'pending', u'parent': u'supportable'}
    {u'amount': 1, u'required': 5}

    >>> Supporter.get_by(Supporter.petition, id)
    [<Supporter [id=u'1-u:42']>]

The same user supports again::

    >>> supporter = {"data": {"user": 42}}
    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/support' % id,
    ...     supporter)
    >>> showInfo(response)
    {u'name': u'pending', u'parent': u'supportable'}
    {u'amount': 1, u'required': 5}

    >>> Supporter.get_by(Supporter.petition, id, size=10)
    [<Supporter [id=u'1-u:42']>]

Support using a telephone number::

    >>> supporter = {"data": {"telephone": '0555 42'}}
    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/support' % id,
    ...     supporter)
    >>> showInfo(response)
    {u'name': u'pending', u'parent': u'supportable'}
    {u'amount': 2, u'required': 5}

    >>> Supporter.get_by(Supporter.petition, id, size=10)
    [<Supporter [id=u'1-u:42']>, <Supporter [id=u'1-t:0555 42']>]

The same telephone number again::

    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/support' % id,
    ...     supporter)
    >>> showInfo(response)
    {u'name': u'pending', u'parent': u'supportable'}
    {u'amount': 2, u'required': 5}

    >>> Supporter.get_by(Supporter.petition, id, size=10)
    [<Supporter [id=u'1-u:42']>, <Supporter [id=u'1-t:0555 42']>]

Approve the petition::

    >>> response = browser.post_json('/v1/petitions/%s/event/approved' % id)
    >>> showInfo(response)
    {u'name': u'active', u'parent': u'supportable'}
    {u'amount': 2, u'required': 5}

    >>> supporter = {"data": {"user": 142}}
    >>> response = browser.post_json(
    ...     '/v1/petitions/%s/event/support' % id,
    ...     supporter)
    >>> showInfo(response)
    {u'name': u'active', u'parent': u'supportable'}
    {u'amount': 3, u'required': 5}

Support until the petition is a winner::


    >>> for userId in range(200, 204):
    ...     supporter = {"data": {"user": userId}}
    ...     response = browser.post_json(
    ...         '/v1/petitions/%s/event/support' % id,
    ...         supporter)
    ...     showInfo(response)
    {u'name': u'active', u'parent': u'supportable'}
    {u'amount': 4, u'required': 5}
    {u'name': u'winner', u'parent': u'supportable'}
    {u'amount': 5, u'required': 5}
    {u'name': u'winner', u'parent': u'supportable'}
    {u'amount': 6, u'required': 5}
    {u'name': u'winner', u'parent': u'supportable'}
    {u'amount': 7, u'required': 5}
