=============
User Document
=============


A user is a `Document`::

    >>> from iris.service.user.document import User
    >>> user = User()
    >>> user
    <User [id=1, '']>

Default dublin core data is set::

    >>> pp(user.dc)
    {
      "created": "...T...+...",
      "modified": "...T...+..."
    }

The state of a user::

    >>> user.state
    'active'

Store the user::

    >>> pp(user.store())
    {
      "_id": "1",
      "_index": "users",
      "_type": "default",
      "_version": 1,
      "created": true
    }

Get the user back from the database::

    >>> user = User.get("1")
    >>> user
    <User [id=1, u'']>
    >>> pp(user.dc)
    {
      "created": "...T...+...",
      "modified": "...T...+..."
    }
    >>> user.state
    u'active'
