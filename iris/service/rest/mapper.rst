===================
REST Service Mapper
===================

Prepare test::

    >>> from iris.service.rest.service import testing_push_state
    >>> testing_push_state()


Implementation
==============

The mapper for the REST service must provide a class which is derived from
RESTMapper::

    >>> from iris.service import rest
    >>> class MyMapper(rest.RESTMapper):
    ...     NAME = 'mymapper'

The RESTMapper class provides a method to get mapper implementations::

    >>> rest.RESTMapper.getMapperImplementation('mymapper')
    <MyMapper object at ...>

A mapper class must provide a NAME::

    >>> class MyInvalidMapper(rest.RESTMapper):
    ...     pass
    Traceback (most recent call last):
    ValueError: MyInvalidMapper.NAME not set

And name must not be duplicates::

    >>> class MyDuplicateMapper(rest.RESTMapper):
    ...     NAME = 'mymapper'
    Traceback (most recent call last):
    NameError: Duplicate name "mymapper", conflicting classes: "MyMapper"-"MyDuplicateMapper"

Test cleanup::

    >>> from iris.service.rest.service import testing_pop_state
    >>> testing_pop_state()
