====================
Generic REST Service
====================

The generic REST API implementation provides access to data by providing
`mapper` implementations. A `RESTMapper` implements the data access layer for
the generic REST endpoint.

The generic REST API is mainly used for the administration access to `raw`
data from the database.

The `RESTService` implementation can only be used with `pyramid_swagger` and
expects the parameters in `request.swagger_data`.

Prepare test::

    >>> from iris.service.rest.service import testing_push_state
    >>> testing_push_state()

    >>> request = get_test_request()

implement a REST service::

    >>> from iris.service import rest
    >>> class MyRESTService(rest.RESTService):
    ...     MAPPER_NAME = 'myrestmapper'

Create a REST service instance::

    >>> request.path = '/v1/admin/myrestmapper/1'
    >>> request.swagger_data = {'contentId': '1'}
    >>> service = MyRESTService(request)
    >>> service.get()
    Traceback (most recent call last):
    BadRequest: Errors.mapper_not_found


Implement a REST Mapper
-----------------------

A mapper must derive from RESTMapper::

    >>> class MyRESTMapper(rest.RESTMapper):
    ...     NAME = 'myrestmapper'
    ...
    ...     def get(self, contentId, resolve, extend):
    ...         return {
    ...             'contentId': contentId
    ...         }
    ...
    ...     def create(self, data, resolve, extend):
    ...         data['id'] = 1
    ...         return data
    ...
    ...     def update(self, contentId, data, resolve, extend):
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

    >>> request.path = '/v1/admin/myrestmapper/1'
    >>> request.swagger_data = {'contentId': '1'}
    >>> pp(service.get())
    {
      "data": {
        "contentId": "1"
      }
    }


REST Create Content
-------------------

Create a new document on the create endpoint::
 
    >>> request.path = '/v1/admin/myrestmapper'
    >>> request.swagger_data = {'data': {'state': 'ready'}}
    >>> pp(service.create())
    {
      "data": {
        "id": 1,
        "state": "ready"
      }
    }


REST Update Content
-------------------

Update an existing document on the update endpoint::

    >>> request.path = '/v1/admin/myrestmapper/2'
    >>> request.swagger_data = {
    ...     'contentId': '2',
    ...     'data': {'state': 'active'}
    ... }
    >>> pp(service.update())
    {
      "data": {
        "id": "2",
        "state": "active"
      }
    }


REST Delete Content
-------------------

Delete an existing document::

    >>> request.path = '/v1/admin/myrestmapper/2'
    >>> request.swagger_data = {'contentId': '2'}
    >>> pp(service.delete())
    {
      "data": {
        "id": "2",
        "state": "test"
      }
    }


REST Query Content
------------------

Query documents::

    >>> request.path = '/v1/admin/myrestmapper'
    >>> request.swagger_data = {}
    >>> pp(service.search())
    {
      "data": {},
      "total": 0
    }


Missing Mapper Functions
------------------------

Missing implementations result in HTTPMethodNotAllowed (405) errors::

    >>> class MyMissingRESTService(rest.RESTService):
    ...     MAPPER_NAME = 'missing'
    >>> service = MyMissingRESTService(request)
    >>> class MyMissingMapper(rest.RESTMapper):
    ...     NAME = 'missing'

    >>> request.path = '/v1/admin/missing/1'
    >>> request.swagger_data = {'contentId': '1'}
    >>> service.get()
    Traceback (most recent call last):
    BadRequest: Errors.method_not_allowed

    >>> request.path = '/v1/admin/missing'
    >>> request.swagger_data = {'data': '1'}
    >>> pp(service.create())
    Traceback (most recent call last):
    BadRequest: Errors.method_not_allowed

    >>> request.path = '/v1/admin/missing/2'
    >>> request.swagger_data = {'contentId': '1', 'data': {}}
    >>> pp(service.update())
    Traceback (most recent call last):
    BadRequest: Errors.method_not_allowed

    >>> request.path = '/v1/admin/missing/2'
    >>> request.swagger_data = {'contentId': '2'}
    >>> pp(service.delete())
    Traceback (most recent call last):
    BadRequest: Errors.method_not_allowed

    >>> request.path = '/v1/admin/missing'
    >>> request.swagger_data = {'limit': 2}
    >>> pp(service.search())
    Traceback (most recent call last):
    BadRequest: Errors.method_not_allowed

Test cleanup::

    >>> from iris.service.rest.service import testing_pop_state
    >>> testing_pop_state()
