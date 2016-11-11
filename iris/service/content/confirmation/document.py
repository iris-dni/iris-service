import time

from lovely.esdb.document import Document
from lovely.esdb.properties import Property

from iris.service.db.dc import dc_defaults, DC_CREATED, DC_EXPIRES, iso_now
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

    context_id = Property(
        doc="""
        A handler specific id which can be used by the specific handler for
        queries.
        """
    )

    data = Property(
        default=lambda: dict(),
        doc="""
        Additional data based on the confirmation handler used.
        """
    )

    response = Property(
        default=lambda: dict(),
        doc="""
        Data which is returned in the confirmation endpoint after a positive
        confirmation. It is the responsibility of the handler to set this
        information.
        """
    )

    debug = Property(
        default=lambda: dict(),
        doc="""
        Additional debug data.
        """
    )

    @property
    def expired(self):
        at = self.dc['expires']
        if at is None:
            return False
        return at <= int(time.time() * 1000)

    @classmethod
    def get_active_context_id(cls, context_id):
        confirmations = Confirmation.search(
            cls.active_context_query(context_id)
        )
        if confirmations['hits']['total'] > 0:
            return confirmations['hits']['hits'][0]
        return None

    @classmethod
    def has_active_context_id(cls, context_id):
        return Confirmation.count(cls.active_context_query(context_id)) > 0

    @classmethod
    def active_context_query(cls, context_id):
        return {
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {
                                "context_id": context_id
                            }
                        },
                        {
                            "term": {
                                "state": 'active'
                            }
                        },
                        {
                            "range": {
                                "dc.expires": {
                                    "gt": iso_now()
                                }
                            }
                        }
                    ]
                }
            }
        }

    def __repr__(self):
        return "<%s [id=%r for %r]>" % (self.__class__.__name__,
                                        self.id,
                                        self.handler)
