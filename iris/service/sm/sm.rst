============
StateMachine
============


    >>> from iris.service.sm import StateMachine

    >>> class MySM(StateMachine):
    ... 
    ...     TRANSITIONS = {
    ...         'draft': {
    ...             'publish': 'published',
    ...             'delete': 'deleted'
    ...         },
    ...         'published': {
    ...             'close': 'closed',
    ...             'delete': 'deleted'
    ...         },
    ...         'deleted': {},
    ...         'closed': {
    ...             'open': 'draft',
    ...         },
    ...     }

    >>> my = MySM('draft')
    >>> my.switch('publish')
    'published'

    >>> my.switch('close')
    'closed'
