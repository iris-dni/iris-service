from lovely.esdb.document import Document
from lovely.esdb.properties import Property
from lovely.essequence import Sequence

from ..db.dc import dc_defaults, DC_CREATED, DC_MODIFIED


# IID generator to create the integer ids for cities
IID = Sequence('cities').next


class City(Document):

    INDEX = 'cities'

    id = Property(primary_key=True, default=IID)

    dc = Property(
        default=dc_defaults(DC_CREATED, DC_MODIFIED),
        doc="Dublin Core data."
    )

    state = Property(
        default='active',
        doc="""
          The current state of the user.
        """
    )

    name = Property(
        default=''
    )

    tags = Property(
        default=lambda: [],
        doc="""
          A list of tags which are searchable.
        """,
    )

    zips = Property(
        default=lambda: [],
        doc="""
          A list of zips.
        """,
    )

    treshold = Property(
        default=0,
        doc="""
          The treshold for the petitions on this city.
        """,
    )

    contact = Property(
        default=lambda: {},
        doc="""
          An object which contains contact information.
        """
    )

    def __repr__(self):
        return "<%s [id=%r, %r]>" % (self.__class__.__name__,
                                     self.id,
                                     self.name)
