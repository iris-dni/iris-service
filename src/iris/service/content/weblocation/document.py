import hashlib

from lovely.esdb.document import Document
from lovely.esdb.properties import Property

from iris.service.db.dc import dc_defaults, DC_CREATED, DC_MODIFIED


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

    def __init__(self, **kwargs):
        if 'url' not in kwargs:
            raise ValueError('url is a required property for WebLocation')
        url = kwargs['url']
        id = self.hash_url(url)
        if "id" in kwargs:
            argsId = kwargs.pop("id")
            if argsId != id:
                raise ValueError("WebLocation id doesn't match url hash!")
        super(WebLocation, self).__init__(id=id, **kwargs)

    @url.setter
    def set_url(self, value):
        if self.id != self.hash_url(value):
            raise ValueError("WebLocation url hash doesn't match id!")
        return value

    @classmethod
    def get_url(cls, url):
        return WebLocation.get(cls.hash_url(url))

    @classmethod
    def mget_urls(cls, urls):
        return WebLocation.mget([cls.hash_url(u) for u in urls])

    @classmethod
    def hash_url(cls, url):
        return hashlib.md5(url).hexdigest()

    def __repr__(self):
        return "<WebLocation %r>" % self.url
