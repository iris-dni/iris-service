==============
Security Token
==============


Setup::

    >>> from iris.service.content.petition.document import Petition
    >>> from iris.service.content.petition import security
    >>> security.PETITION_SECRET_KEY
    'strong-petition-secret'

    >>> petition = Petition(id='foobar')

Test the helper function::

    >>> security._generate_signature(petition.id, 12345)
    u'69d4e4e1b6b8c3fcab09aed83553585fa11d58a5,12345'

Test the 'verification'::

    >>> token = security.generate_petition_token(petition)

    >>> request = get_test_request()
    >>> request.swagger_data = {'petition': petition.id,
    ...                         'token': token}
    >>> security.verify_petition_token(request)
    True


Wrong token::

    >>> import base64
    >>> request.swagger_data = {'petition': petition.id,
    ...                         'token': base64.b64encode('different,1234')}
    >>> security.verify_petition_token(request)
    False

Not base64 encoded::

    >>> request.swagger_data = {'petition': petition.id,
    ...                         'token': 'different,1234'}
    >>> security.verify_petition_token(request)
    False

Base64 encoded but missing timestamp::

    >>> request.swagger_data = {'petition': petition.id,
    ...                         'token': base64.b64encode('different')}
    >>> security.verify_petition_token(request)
    False

No matching ID::

    >>> request.swagger_data = {'petition': ['foo', 'bar', 'baz'],
    ...                         'token': token}
    >>> security.verify_petition_token(request)
    False
