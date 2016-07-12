===========================
Dublin Core Data Management
===========================

The `dc` module allows to manage dublin code (dc) data for `Documents`.

The dc module is in the db package::

    >>> from iris.service.db import dc


Create default values
=====================

dc_defaults returns a method which can be called to create a default dubli
core dict::

    >>> default_generator = dc.dc_defaults()
    >>> default_generator()
    {}

The default fields can be selected as args::

    >>> pp(dc.dc_defaults('modified')())
    {
      "modified": "...T...+..."
    }

    >>> pp(dc.dc_defaults('modified', 'created', 'effective', 'expires')())
    {
      "created": "...T...+...",
      "effective": null,
      "expires": null,
      "modified": "...T...+..."
    }

Using kwargs it is possible to provide the default value::

    >>> pp(dc.dc_defaults(modified=None)())
    {
      "modified": null
    }

It can be mixed::

    >>> pp(dc.dc_defaults('created', modified=None)())
    {
      "created": "...T...+...",
      "modified": null
    }

It is also possible to provide a method as default value::

    >>> def myDefaultCreator():
    ...     return 'my default'
    >>> pp(dc.dc_defaults(modified=myDefaultCreator)())
    {
      "modified": "my default"
    }

Unknwon properties are not allowed::

    >>> pp(dc.dc_defaults('unknown')())
    Traceback (most recent call last):
    KeyError: 'dc key "unknown" not allowed'

A special generator which sets all properties to the defaults::

    >>> pp(dc.dc_defaults_all()())
    {
      "created": "...T...+...",
      "effective": null,
      "expires": null,
      "modified": "...T...+..."
    }
