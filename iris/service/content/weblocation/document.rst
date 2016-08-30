====================
WebLocation Document
====================

A WebLocation is a `Document`::

    >>> from iris.service.content.weblocation import WebLocation
    >>> weblocation = WebLocation(url="http://www.iris.com")
    >>> weblocation
    <WebLocation 'http://www.iris.com'>
    >>> weblocation.id
    'cd126eaf1870967a2f3d724ee935b379'

    >>> pp(weblocation.dc)
    {
      "created": "...T...+...",
      "modified": "...T...+..."
    }

    >>> weblocation.url
    'http://www.iris.com'

    >>> weblocation.state
    'visible'

    >>> weblocation.og is None
    True

Store it::

    >>> _ = weblocation.store()

    >>> WebLocation.get(weblocation.id).url == weblocation.url
    True
