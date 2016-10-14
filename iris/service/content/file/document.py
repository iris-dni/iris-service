from lovely.esdb.document import Document
from lovely.esdb.properties import Property

from iris.service.db.dc import dc_defaults, DC_CREATED, DC_MODIFIED


class StorageType(object):
    S3 = "s3"


class File(Document):
    """A file in the database.

    This is a meta data container for the file. The file remains in an external
    storage.
    """

    INDEX = 'files'

    id = Property(primary_key=True)

    dc = Property(
        default=dc_defaults(DC_CREATED, DC_MODIFIED),
        doc="Dublin Core data."
    )

    state = Property()

    original_name = Property()

    owner_id = Property()

    storage_type = Property()

    content_type = Property()
