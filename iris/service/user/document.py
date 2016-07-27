from lovely.esdb.document import Document
from lovely.esdb.properties import Property
from lovely.essequence import Sequence

from ..db.dc import dc_defaults, DC_CREATED, DC_MODIFIED


# IID generator to create the integer ids for users
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

    trusted = Property(
        default=False,
        doc="Trusted users have additional privilegs"
    )

    roles = Property(
        default=[],
        doc="""
          The roles are simple strings used for access control.
        """
    )

    @roles.getter
    def get_roles(self, value):
        """adds internal roles

        trusted: if the trusted flag is set to True
        """
        more = []
        if self.trusted:
            more.append('trusted')
        return value + more

    @roles.setter
    def set_roles(self, value):
        """Removes the trusted role if provided
        """
        if 'trusted' in value:
            value.remove('trusted')
        return value

    sso = Property(
        default=[],
        doc="""
          Data for the different SSO providers used by this user.
        """
    )

    @classmethod
    def get_or_create_by_sso_data(cls, email, **kwargs):
        user = cls.get_by(cls.email, email)
        if user is None:
            user = User(email=email, **kwargs)
        user.store(refresh=True)
        return user

    def __repr__(self):
        return "<%s [id=%r, %r]>" % (self.__class__.__name__,
                                     self.id,
                                     self.email)
