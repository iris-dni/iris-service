import copy

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

    tags = Property(
        default=lambda: copy.copy([]),
        doc="""
          A list of tags which are searchable.
        """,
    )

    title = Property(
        default=''
    )

    city = Property(
        default=None,
        doc="""
          A reference to a city (id).
        """
    )

    type = Property(
        default='',
        doc="""
          A string defined by the frontend (no internal meaning).
        """
    )

    description = Property(
        default=''
    )

    suggested_solution = Property(
        default=''
    )

    images = Property(
        default=[],
        doc="A list of file ids."
    )

    links = Property(
        default=lambda: copy.copy([]),
        doc="A list of location ids."
    )

    videos = Property(
        default=lambda: copy.copy([]),
        doc="A list of location ids to youtube videos."
    )

    connected_locations = Property(
        default=lambda: copy.copy([]),
        doc="""
          A list of location ids to location which are connected to this
          petition.
        """
    )

    signatures = Property(
        default=lambda: copy.copy({}),
        doc="""
          An object which contains information about the signatures of the
          petition.
        """
    )

    owner = Property(
        default=None
    )

    response_token = Property(
        default=None
    )

    def __repr__(self):
        return "<%s [id=%r]>" % (self.__class__.__name__, self.id)
