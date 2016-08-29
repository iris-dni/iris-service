from lovely.esdb.document import Document
from lovely.esdb.properties import Property

from iris.service.db.dc import dc_defaults, DC_CREATED, DC_MODIFIED


class WebLocation(Document):
    """A web location (URL) in the database

    TODO: needs to be completed
    """

    INDEX = 'weblocations'

    id = Property(primary_key=True)

    dc = Property(
        default=dc_defaults(DC_CREATED, DC_MODIFIED),
        doc="Dublin Core data."
    )

    url = Property(
        doc="The URL of the location"
    )

    og = Property(
        doc="Open Graph data"
    )
