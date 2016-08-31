=================
SSOToken Document
=================

SSOTokens store the sso messaage with the apikey which was used to create the
sso message::

    >>> from iris.service.auth.sso import sign_message
    >>> sso = sign_message({'some': 'data'}, 'test_public_api_key')

SSOTokens are managed via the SSOToken document class::

    >>> from iris.service.auth import SSOToken
    >>> token = SSOToken(sso=sso, apikey='test_public_api_key')
    >>> token
    <SSOToken [token='2688dba5a677a8c704f1ed1e248bf526']>
    >>> token.sso == sso
    True
    >>> token.apikey
    'test_public_api_key'

    >>> pp(token.store())
    {
      "_id": "2688dba5a677a8c704f1ed1e248bf526",
      "_index": "ssotokens",
      "_type": "default",
      "_version": 1,
      "created": true
    }

    >>> token.dc['created']
    '20...T...+...'


Resolve a token
---------------

With a token the sso and apikey can be resolved::

    >>> SSOToken.resolve(token.token) == (sso, 'test_public_api_key')
    True

Now because the token is consumed it is removed from the database::

    >>> SSOToken.get(token.token) is None
    True

and can no longer be resolved::

    >>> SSOToken.resolve(token.token) is None
    True
