==============
File Relations
==============

The current implementation of the cleanup script checks the usage of each file
by the currently known relation porperties pointing to the `File` class.

CAUTION!: Whenever the following test fails alter the cleanup script to care
          about newly added file relations! Ignoring this will cause data
          loss!

Determine all relation properties with `File` as remote_class::

    >>> from lovely.esdb.properties.relation import RelationBase
    >>> def isFileRelation(obj):
    ...     return (isinstance(obj, RelationBase)
    ...             and obj.remote_class is File)

    >>> import inspect
    >>> from lovely.esdb.document import document
    >>> from iris.service.content.file.document import File
    >>> for cls in document.DOCUMENT_CLASSES.values():
    ...     for (name, prop) in inspect.getmembers(cls, isFileRelation):
    ...         print cls.__module__ + "." + cls.__name__ + "." + name
    iris.service.content.petition.document.Petition.images


