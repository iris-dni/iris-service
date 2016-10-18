===================
File Document Tests
===================

File objects are not real file object, but objects containing meta data for
files stored on an external location (e.g. S3).

Create a user::

    >>> from iris.service.content.user.document import User
    >>> user = User()

Create a file object with valid data::

    >>> from iris.service.content.file.document import File, StorageType
    >>> f = File(
    ...     id="some_hash",
    ...     state='visible',
    ...     original_name="sample.txt",
    ...     owner=user,
    ...     storage_type=StorageType.S3,
    ...     content_type="text/plain"
    ... )
    >>> _ = f.store()

The DC created and modified dates are set::

    >>> print_json(f.dc)
    {
      "created": "...",
      "modified": "..."
    }