===================
REST Service Mapper
===================

Prepare test::

    >>> from iris.service.service import rest
    >>> rest.testing_push_state()


Implementation
==============

The mapper for the REST service must provide a class which is derived from
RESTMapper::

    >>> from iris.service.service.rest import RESTMapper

    >>> class MyMapper(RESTMapper):
    ...     NAME = 'mymapper'

The class is registered with the NAME::

    >>> RESTMapper._MAPPER_REGISTRY
    {'mymapper': <class 'MyMapper'>}

The RESTMapper class provides a method to get mapper implementations::

    >>> RESTMapper.getMapperImplementation('mymapper')
    <MyMapper object at ...>

A mapper class must provide a NAME::

    >>> class MyInvalidMapper(RESTMapper):
    ...     pass
    Traceback (most recent call last):
    ValueError: MyInvalidMapper.NAME not set

And name must not be duplicates::

    >>> class MyDuplicateMapper(RESTMapper):
    ...     NAME = 'mymapper'
    Traceback (most recent call last):
    NameError: Duplicate name "mymapper", conflicting classes: "MyMapper"-"MyDuplicateMapper"

Test cleanup::

    >>> rest.testing_pop_state()
