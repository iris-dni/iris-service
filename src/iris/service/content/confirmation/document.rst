=====================
Confirmation Document
=====================


A Confirmation is a `Document`::

    >>> from iris.service.content.confirmation import Confirmation
    >>> confirmation = Confirmation(
    ...     handler='test',
    ...     data={
    ...         u'whatever': u'you',
    ...         u'like': True
    ...     },
    ...     debug={
    ...         u'handlers': u'can store any debug information'
    ...     }
    ... )
    >>> confirmation
    <Confirmation [id=u'1n3gf' for 'test']>

    >>> sorted(confirmation.dc.keys())
    ['created', 'expires']
    >>> confirmation.state
    'active'
    >>> confirmation.data
    {u'like': True, u'whatever': u'you'}
    >>> confirmation.debug
    {u'handlers': u'can store any debug information'}

    >>> _ = confirmation.store()

    >>> confirmation = Confirmation.get(confirmation.id)
    >>> confirmation
    <Confirmation [id=u'1n3gf' for u'test']>

    >>> sorted(confirmation.dc.keys())
    [u'created', u'expires']
    >>> confirmation.state
    u'active'
    >>> confirmation.data
    {u'like': True, u'whatever': u'you'}
    >>> confirmation.debug
    {u'handlers': u'can store any debug information'}
