from lovely.esdb.document import Document
from lovely.esdb.properties import Property
from lovely.essequence import Sequence

from ..db.dc import dc_defaults, DC_CREATED, DC_MODIFIED


# IID generator to create the integer ids for petitions
IID = Sequence('users').next


class User(Document):

    INDEX = 'users'

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

    email = Property(
        default=''
    )

    firstname = Property(
        default=''
    )

    lastname = Property(
        default=''
    )

    roles = Property(
        default=[],
        doc="""
          The roles are simple strings used for access control.
        """
    )

    sso = Property(
        default=[],
        doc="""
          Data for the different SSO providers used by this user.
        """
    )

    def __repr__(self):
        return "<%s [id=%r, %r]>" % (self.__class__.__name__,
                                     self.id,
                                     self.email)
