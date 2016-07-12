from lovely.esdb.document import Document
from lovely.esdb.properties import Property
from lovely.essequence import Sequence

from ..db.dc import dc_defaults_all


# IID generator to create the integer ids for petitions
IID = Sequence('petitions').next


class Petition(Document):
    INDEX = 'petitions'

    id = Property(primary_key=True, default=IID)

    dc = Property(
        default=dc_defaults_all(),
        doc="Dublin Core data."
    )

    state = Property(
        default='draft',
        doc="""
          The current state of the petition.
          The state is controlled via a state machine.
        """
    )

    def __repr__(self):
        return "<%s [id=%r]>" % (self.__class__.__name__, self.id)
