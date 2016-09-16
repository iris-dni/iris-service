===================
Tests for Elections
===================

The election module can be used to coordinate services over multiple
processes. The election coordination is done using a database entry which
contains the id of an elected instance.


Use The Elector
===============

An elector is an instance of the class Elector and has a name. Electors with
the same name are used to together. Only one instance of all electors with the
same name is the elected instance::

    >>> from iris.service.elector import Elector
    >>> elector = Elector("test")

An elector has an ident which is unique for the instance::

    >>> elector.ident != Elector("test").ident
    True

The first elector which calls "is_elected" becomes the elected one::

    >>> elector.is_elected
    True

Other electors for the same name are not elected::

    >>> elector2 = Elector("test")
    >>> elector2.is_elected
    False

Different elector names have their own election::

    >>> elector3 = Elector("other")
    >>> elector3.is_elected
    True

    >>> elector.is_elected
    True
    >>> elector2.is_elected
    False


Election Expire
===============

Elections expire if they are not used.

To test this behaviour we provide a fake time module::

    >>> class FakeTime(object):
    ...     def __init__(self, t):
    ...         self._t = t
    ...     def time(self):
    ...         return self._t

And use it for the elector module with the current time set to 0::

    >>> from iris.service import elector as elector_module
    >>> elector_module.time = FakeTime(0.0)
    >>> elector_module.time.time()
    0.0

A new elector instance set the expire time::

    >>> el1 = Elector("expire")
    >>> el1.election.until
    30000
    >>> elector_module.TTL
    30000

Election time is extended when is_elected is used::

    >>> elector_module.time._t = 16.0
    >>> el1.is_elected
    True
    >>> el1.election.until
    46000

If the elected elector is not used another elector will be elected::

    >>> el2 = Elector("expire")
    >>> el2.is_elected
    False

    >>> elector_module.time._t = 47.0
    >>> el2.is_elected
    True
    >>> el1.is_elected
    False
