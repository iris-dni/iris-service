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

The url is not changeable::

    >>> weblocation.url = 'www.nowhere.com'
    Traceback (most recent call last):
    ValueError: WebLocation url hash doesn't match id!

    >>> weblocation.url = "http://www.iris.com"

Store it::

    >>> _ = weblocation.store()

    >>> WebLocation.get(weblocation.id).url == weblocation.url
    True


Get WebLocations by url
-----------------------

Build some locations::

    >>> for i in range(5):
    ...     _ = WebLocation(url='http://www.%s.com' % i).store()
    >>> _ = WebLocation.refresh()

    >>> locations = WebLocation.mget_urls(['http://www.1.com', 'http://www.3.com'])
    >>> locations
    [<WebLocation u'http://www.1.com'>, <WebLocation u'http://www.3.com'>]
