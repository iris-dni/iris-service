=============
City Document
=============


A city is a `Document`::

    >>> from iris.service.city.document import City
    >>> city = City()
    >>> city
    <City [id=1, '']>

    >>> pp(city.dc)
    {
      "created": "...T...+...",
      "modified": "...T...+..."
    }
    >>> city.state
    'active'
    >>> city.name
    ''
    >>> city.tags
    []
    >>> city.zips
    []
    >>> city.treshold
    0
    >>> city.contact
    {}

Store the city::

    >>> pp(city.store())
    {
      "_id": "1",
      "_index": "cities",
      "_type": "default",
      "_version": 1,
      "created": true
    }

Get the city back from the database::

    >>> city = City.get(1)
    >>> city
    <City [id=1, u'']>
    >>> pp(city.dc)
    {
      "created": "...T...+...",
      "modified": "...T...+..."
    }
    >>> city.state
    u'active'
