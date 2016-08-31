from lovely.esdb.document import Document
from lovely.esdb.properties import Property
from lovely.essequence import Sequence

from iris.service.db.dc import dc_defaults, DC_CREATED, DC_MODIFIED


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

    roles = Property(
        default=lambda: [],
        doc="""
          The roles are simple strings used for access control.
        """
    )

    sso = Property(
        name="sso",
        default=lambda: [],
        doc="""
          Data for the different SSO providers used by this user.
        """
    )

    @sso.setter
    def set_sso(self, value):
        if isinstance(value, dict):
            provider = value['provider']
            original = self.sso
            found = False
            for p in original:
                if p['provider'] == provider:
                    p.update(value)
                    found = True
                    break
            if not found:
                original.append(value)
            return original
        return value

    @classmethod
    def update_or_create_by_email(cls, email, **kwargs):
        user = cls.get_by(cls.email, email)
        if user:
            user = user[0]
        else:
            user = User(email=email)
        for k, v in kwargs.iteritems():
            setattr(user, k, v)
        user.store(refresh=True)
        return user

    def __repr__(self):
        return "<%s [id=%r, %r]>" % (self.__class__.__name__,
                                     self.id,
                                     self.email)
