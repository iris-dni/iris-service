==========
Cleanup S3
==========


Setup for mock S3::

    >>> class MockS3(object):
    ...     def __init__(self):
    ...         self.fail = False
    ...         self.deleted_on_s3 = []
    ...     def Object(self, *args):
    ...         return MockS3Object(self, *args)

    >>> class MockS3Object(object):
    ...     def __init__(self, s3, bucket, key):
    ...         self.s3 = s3
    ...         self.bucket = bucket
    ...         self.key = key
    ...     def delete(self):
    ...         self.s3.deleted_on_s3.append(self.key)
    ...     def wait_until_not_exists(self):
    ...         if self.s3.fail:
    ...             raise Exception("WaitError")


Create a user::

    >>> from iris.service.content.user.document import User
    >>> user = User()

    >>> user = creators.user(email='42@email.com')
    >>> _ = user.store()


Create a file object with valid data::

    >>> from iris.service.content.file.document import File, StorageType

    >>> def create_file(iid):
    ...     f = File(
    ...         id=iid,
    ...         state='visible',
    ...         original_name="sample.txt",
    ...         owner=user,
    ...         storage_type=StorageType.S3,
    ...         content_type="text/plain"
    ...     )
    ...     _ = f.store()
    ...     return f

Create some files::

    >>> f1 = create_file("hash1")
    >>> f2 = create_file("hash2")
    >>> f3 = create_file("hash3")

    >>> _ = File.refresh()

Initialize a cleaner::

    >>> from iris.scripts.cleanup_s3 import S3Cleaner
    >>> cleaner = S3Cleaner(
    ...     hosts=['127.0.0.1:19342'],
    ...     min_age=1,
    ...     bucket='stub',
    ...     aws_access_key_id='key',
    ...     aws_secret_access_key='secret',
    ...     region_name='stub',
    ... )

Use the mocked S3 service::

    >>> cleaner.s3 = MockS3()

This cleaner will care about images older than the given `min_age`. So it will
not find any files::

    >>> len(list(cleaner._s3_files()))
    0

Se the `min_age` to 0 to find all test files::

    >>> cleaner.min_age = 0
    >>> len(list(cleaner._s3_files()))
    3
    >>> [f['_id'] for f in cleaner._s3_files()]
    [u'hash1', u'hash2', u'hash3']

None of these files are in use yet::

    >>> cleaner._in_use('hash1')
    False
    >>> cleaner._in_use('hash2')
    False
    >>> cleaner._in_use('hash3')
    False

Create one petition with a relation to an image::

    >>> peti = creators.petition(title='tester', images=[f1])
    >>> _ = peti.store()

Now file 'hash1' is in use but the other files aren't::

    >>> cleaner._in_use('hash1')
    True
    >>> cleaner._in_use('hash2')
    False
    >>> cleaner._in_use('hash3')
    False

Create another petition with a relation to two images::

    >>> peti = creators.petition(title='tester', images=[f1, f3])
    >>> _ = peti.store()

Now file 'hash3' in in use as well::

    >>> cleaner._in_use('hash1')
    True
    >>> cleaner._in_use('hash2')
    False
    >>> cleaner._in_use('hash3')
    True

Deleting a file does not do anything if `dry_run` was set::

    >>> cleaner.dry_run = True
    >>> cleaner._delete('hash1')

    >>> cleaner.s3.deleted_on_s3
    []

Without the `dry_run` option the files will get deleted on S3 and in Crate::

    >>> f4 = create_file("hash4")
    >>> _ = File.refresh()

    >>> cleaner.dry_run = False
    >>> cleaner._delete(u'hash4')

    >>> cleaner.s3.deleted_on_s3
    [u'hash4']

    >>> File.get("hash4") is None
    True

    >>> _ = File.refresh()

If a file couldn't been deleted on S3 for any reason the S3 client will raise
an exception hence the file will remain in crate as well::

    >>> cleaner.s3.fail = True
    >>> cleaner._delete('hash1')
    Traceback (most recent call last):
    Exception: WaitError

    >>> File.get("hash1") is not None
    True

Run an actual cleanup::

    >>> cleaner.s3 = MockS3()
    >>> cleaner.clean()
    Deleted:	... 	Kept:	...

File 2 (with hash "hash2") has been deleted, File 1 and File 3 not::

    >>> File.get("hash1") is not None
    True

    >>> File.get("hash2") is not None
    False

    >>> File.get("hash3") is not None
    True

The file 2 has been deleted on S3::

    >>> cleaner.s3.deleted_on_s3
    [u'hash2']
