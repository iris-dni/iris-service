import hashlib

from lovely.esdb.document import Document
from lovely.esdb.properties import Property

from iris.service.db.dc import dc_defaults, DC_CREATED, DC_MODIFIED


def hash_url(url):
    return hashlib.md5(url).hexdigest()


class WebLocation(Document):
    """A web location (URL) in the database

    The database id of a WebLocation is the md5 hash of its url.
    It is not allowed to change the url of a WebLocation because this would
    change its primary key.
    """

    INDEX = 'weblocations'

    id = Property(primary_key=True)

    dc = Property(
        default=dc_defaults(DC_CREATED, DC_MODIFIED),
        doc="Dublin Core data."
    )

    state = Property(
        default='visible',
        doc="The state of the location"
    )

    url = Property(
        doc="The URL of the location"
    )

    og = Property(
        doc="Open Graph data"
    )

    def __init__(self, url=object, **kwargs):
        id = hash_url(url)
        if "id" in kwargs:
            argsId = kwargs.pop("id")
            if argsId != id:
                raise ValueError("WebLocation id doesn't match url hash!")
        super(WebLocation, self).__init__(id=id, url=url, **kwargs)

    @url.setter
    def set_url(self, value):
        if self.id != hash_url(value):
            raise ValueError("WebLocation url hash doesn't match id!")
        return value

    def __repr__(self):
        return "<WebLocation %r>" % self.url
