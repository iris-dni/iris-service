====================
REST Document Mapper
====================

The REST mapper for documents allows a mapper to access the data defined by a
`lovely.esdb.document` document.


Define a Document Mapper
------------------------

First we implement a dummy document for simpler testing::

    >>> class DummyDocument(object):
    ...
    ...     def __init__(self, **kwargs):
    ...         self.doc = kwargs
    ...
    ...     @classmethod
    ...     def get(cls, id):
    ...         print 'get(%r, %r)' % (cls.__name__, id)
    ...         return DummyDocument(id=id)
    ...     @classmethod
    ...     def mget(cls, ids):
    ...         print 'mget(%r, %r)' % (cls.__name__, ids)
    ...         return [DummyDocument(id=id) for id in ids]
    ...     def delete(self, **kwargs):
    ...         print 'delete(%r)' % kwargs
    ...         return self
    ...     def store(self, **kwargs):
    ...         print 'store(%r)' % kwargs
    ...         return {}
    ...     @classmethod
    ...     def search(cls, query, **kwargs):
    ...         print 'search(%r)' % kwargs
    ...         print 'query=%s' % query
    ...         return {
    ...             'hits': {
    ...                 'hits': [cls(id='1'), cls(id='2')],
    ...                 'total': 2
    ...             }
    ...         }
    ...     def get_source(self):
    ...         return self.doc

Now with the `DocumentRESTMapperMixin` we can implement a mapper for a
`Document` implementation::

    >>> from iris.service.rest import DocumentRESTMapperMixin
    >>> class TestMapper(DocumentRESTMapperMixin):
    ...
    ...     DOC_CLASS = DummyDocument
    ...     request = get_test_request()

    >>> mapper = TestMapper()
    >>> mapper.get('1')
    get('DummyDocument', '1')
    {'id': '1'}

    >>> mapper.get(['1', '2'])
    mget('DummyDocument', ['1', '2'])
    [{'id': '1'}, {'id': '2'}]

    >>> mapper.create({'data': {'state': 'test'}})
    store({'refresh': True})
    {'state': 'test'}

    >>> mapper.update('1', {'data': {'state': 'test'}})
    get('DummyDocument', '1')
    store({'refresh': True})
    {'id': '1'}

    >>> mapper.delete('1')
    get('DummyDocument', '1')
    delete({'refresh': True})
    {'id': '1'}

A searchable document mapper::

    >>> from iris.service.rest import SearchableDocumentRESTMapperMixin
    >>> class SearchableTestMapper(DocumentRESTMapperMixin,
    ...                            SearchableDocumentRESTMapperMixin
    ...                           ):
    ...
    ...     DOC_CLASS = DummyDocument
    ...     request = get_test_request()

    >>> mapper = SearchableTestMapper()
    >>> mapper.search(limit='5')
    search({})
    query={'sort': ['_score'], 'query': {'filtered': {'filter': {'bool': {'must': []}}, 'query': {'bool': {'must': []}}}}, 'from': 0, 'size': '5'}
    {'total': 2, 'data': [{'id': '1'}, {'id': '2'}]}
