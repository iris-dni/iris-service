import time

from lovely.esdb.document import Document
from lovely.esdb.properties import Property

from iris.service.db.dc import dc_defaults, DC_CREATED, DC_EXPIRES
from iris.service.db.sequence import IID_SHORTED


class Confirmation(Document):
    """Confirmation to manage external async jobs

    A confirmation stores a confirmation id and a handler used to manage the
    confirmation.
    """

    INDEX = 'confirmations'

    def __init__(self, handler, **kwargs):
        super(Confirmation, self).__init__(
            handler=handler,
            **kwargs
        )

    id = Property(primary_key=True, default=IID_SHORTED)

    dc = Property(
        default=dc_defaults(DC_CREATED, DC_EXPIRES),
        doc="Dublin Core data."
    )

    state = Property(
        default='active',
    )

    handler = Property(
        doc="""
        The confirmation type is used to find an implementation to manage the
        confirmation.
        """
    )

    data = Property(
        default=lambda: dict(),
        doc="""
        Additional data based on the confirmation handler used.
        """
    )

    @property
    def expired(self):
        at = self.dc['expires']
        if at is None:
            return False
        return at <= int(time.time() * 1000)

    def __repr__(self):
        return "<%s [id=%r for %r]>" % (self.__class__.__name__,
                                        self.id,
                                        self.handler)
