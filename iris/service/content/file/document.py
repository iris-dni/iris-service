from lovely.esdb.document import Document
from lovely.esdb.properties import Property, LocalRelation

from iris.service.db.dc import dc_defaults, DC_CREATED, DC_MODIFIED
from .tempstorage import get_temp_upload_path


IMAGE_PROXY_URL = None


class StorageType(object):
    S3 = "s3"
    TMP = "tmp"


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

    state = Property(
        doc="The state of the file (visible/hidden)"
    )

    original_name = Property(
        doc="The original file name before upload"
    )

    _owner_id = Property(
        name="owner_id",
        doc="The ID of the user/session user who uploaded the file"
    )
    owner = LocalRelation('_owner_id', 'User.id')

    storage_type = Property(
        doc="""The kind of storage that has been used for the file.

        `s3` for files stored on S3, `tmp` for files stored in a temporary
        folder (used for local/testing environments).
        """
    )

    content_type = Property(
        doc="The file's guessed MIME type (e.g. `text/plain`, `image/jpeg`)"
    )

    info = Property(
        doc="""Additional file info dependent on file type.

        E.g. contains width and height of an image files.
        """,
        default=lambda: {},
    )

    @property
    def original_url(self):
        """The original URL of the file without image proxy.
        """
        if self.storage_type == StorageType.S3:
            from .s3 import get_s3_url
            return get_s3_url(self.id)
        elif self.storage_type == StorageType.TMP:
            # for local environment or testing
            return "file://%s/%s" % (get_temp_upload_path(), self.id)
        return None

    @property
    def image_proxy_base_url(self):
        """The image proxy base URL of the file.

        This URL must be extended with further pilbox parameters and a
        signature.
        """
        return "%s/?url=%s" % (IMAGE_PROXY_URL, self.id)

    def get_source(self):
        res = super(File, self).get_source()
        res['original_url'] = self.original_url
        res['image_proxy_base_url'] = self.image_proxy_base_url
        return res


def includeme(config):
    global IMAGE_PROXY_URL
    settings = config.get_settings()
    IMAGE_PROXY_URL = settings['imageproxy.url']
