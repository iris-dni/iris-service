============
API Extender
============

Extenders allow the API to extend document data with additional information.

Import the extender class::

    >>> from iris.service.rest.extender import APIExtender


Extender Implementation
=======================

An extender is a class which is instantiated with the request and the
documents to extend. The extend method is called with the already transformed
documents::

    >>> class TestExtender(object):
    ...     """Provides the lowercased title as an extension property"""
    ...
    ...     def __init__(self, request, docs):
    ...         self.request = request
    ...         self.docs = docs
    ...
    ...     def extend(self, docs):
    ...         for doc in docs:
    ...             APIExtender.applyExtensionData(doc, 'title', doc['title'].lower())

An extender must be registered with a name::

    >>> APIExtender.register('test', TestExtender)


API Extender Use
================

First create an extender instance for the documents::

    >>> request = get_test_request()
    >>> docs = [{"title": "Test1"}]
    >>> extender = APIExtender(request, docs, ['test'])

The unextended data::

    >>> print_json(docs)
    [
      {
        "title": "Test1"
      }
    ]

Then extend the data to the transformed documents::

    >>> extender.extend(docs)

The extended data::

    >>> print_json(docs)
    [
      {
        "extensions": {
          "title": "test1"
        },
        "title": "Test1"
      }
    ]
