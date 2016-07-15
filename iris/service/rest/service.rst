====================
Generic REST Service
====================

The generic REST API implementation provides access to data by providing
`mapper` implementations. A `RESTMapper` implements the data access layer for
the generic REST endpoint.

The generic REST API is mainly used for the administration access to `raw`
data from the database.

Prepare test::

    >>> from iris.service.rest.service import testing_push_state
    >>> testing_push_state()

    >>> request = get_test_request()

Create a REST service instance::

    >>> from iris.service import rest
    >>> service = rest.RESTService(request)
    >>> service.get('myrestmapper', '1')
    Traceback (most recent call last):
    BadRequest: Errors.mapper_not_found


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
    ...     def delete(self, contentId):
    ...         return {
    ...             'id': contentId,
    ...             'state': 'test'
    ...         }
    ...
    ...     def search(self, **kwargs):
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


REST Delete Content
-------------------

Delete an existing document::

    >>> pp(service.delete('myrestmapper', '2'))
    {
      "data": {
        "id": "2",
        "state": "test"
      }
    }


REST Query Content
------------------

Query documents::

    >>> pp(service.search('myrestmapper'))
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
    BadRequest: MyMissingMapper.get

    >>> pp(service.create('missing', {'state': 'ready'}))
    Traceback (most recent call last):
    BadRequest: MyMissingMapper.create

    >>> pp(service.update('missing', '2', {'state': 'active'}))
    Traceback (most recent call last):
    BadRequest: MyMissingMapper.update

    >>> pp(service.delete('missing', '2'))
    Traceback (most recent call last):
    BadRequest: MyMissingMapper.delete

    >>> pp(service.search('missing'))
    Traceback (most recent call last):
    BadRequest: MyMissingMapper.search

Test cleanup::

    >>> from iris.service.rest.service import testing_pop_state
    >>> testing_pop_state()
