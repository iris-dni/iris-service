====================
Generic REST Service
====================

The generic REST API implementation provides access to data by providing
`mapper` implementations. A `RESTMapper` implements the data access layer for
the generic REST endpoint.

The generic REST API is mainly used for the administration access to `raw`
data from the database.

Prepare test::

    >>> from iris.service.service import rest
    >>> rest.testing_push_state()

    >>> request = get_test_request()

Create a REST service instance::

    >>> service = rest.RESTService(request)
    >>> service.get('myrestmapper', '1')
    Traceback (most recent call last):
    HTTPNotFound: Mapper 'myrestmapper' not found


Implement a REST Mapper
-----------------------

A mapper must derive from RESTMapper::

    >>> class MyRESTMapper(rest.RESTMapper):
    ...     NAME = 'myrestmapper'
    ...
    ...     def get(self, contentId):
    ...         return {
    ...             'contentId': contentId
    ...         }
    ...
    ...     def create(self, data):
    ...         data['id'] = 1
    ...         return data
    ...
    ...     def update(self, contentId, data):
    ...         data['id'] = contentId
    ...         return data
    ...
    ...     def query(self, **kwargs):
    ...         return {'data': kwargs, 'total': 0}


REST Get Content
----------------

Get a document by id. The get method of the service must be called with the
mapper name as its first paramter::

    >>> pp(service.get('myrestmapper', '1'))
    {
      "data": {
        "contentId": "1"
      }
    }


REST Create Content
-------------------

Create a new document on the create endpoint::

    >>> pp(service.create('myrestmapper', {'state': 'ready'}))
    {
      "data": {
        "id": 1,
        "state": "ready"
      }
    }


REST Update Content
-------------------

Update an existing document on the update endpoint::

    >>> pp(service.update('myrestmapper', '2', {'state': 'active'}))
    {
      "data": {
        "id": "2",
        "state": "active"
      }
    }


REST Query Content
------------------

Query documents::

    >>> pp(service.query('myrestmapper'))
    {
      "data": {},
      "total": 0
    }


Missing Mapper Functions
------------------------

Missing implementations result in HTTPMethodNotAllowed (405) errors::

    >>> class MyMissingMapper(rest.RESTMapper):
    ...     NAME = 'missing'

    >>> service.get('missing', '1')
    Traceback (most recent call last):
    HTTPMethodNotAllowed: MyMissingMapper.get

    >>> pp(service.create('missing', {'state': 'ready'}))
    Traceback (most recent call last):
    HTTPMethodNotAllowed: MyMissingMapper.create

    >>> pp(service.update('missing', '2', {'state': 'active'}))
    Traceback (most recent call last):
    HTTPMethodNotAllowed: MyMissingMapper.update

    >>> pp(service.query('missing'))
    Traceback (most recent call last):
    HTTPMethodNotAllowed: MyMissingMapper.query

Test cleanup::

    >>> rest.testing_pop_state()
