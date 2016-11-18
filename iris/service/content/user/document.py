import random

from lovely.esdb.document import Document
from lovely.esdb.properties import Property

from iris.service.security import acl

from iris.service.db.dc import dc_defaults, DC_CREATED, DC_MODIFIED
from iris.service.db.sequence import IID_SHORTED


class User(Document):

    INDEX = 'users'

    id = Property(primary_key=True, default=IID_SHORTED)

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

    email_trusted = Property(
        default=False
    )

    mobile = Property(
        default=''
    )

    mobile_trusted = Property(
        default=False
    )

    firstname = Property(default='')
    lastname = Property(default='')
    street = Property(default='')
    zip = Property(default='')
    town = Property(default='')

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
            if kwargs.get('email_trusted') is False:
                # don't allow to overwrite the email_trusted flag with false
                del kwargs['email_trusted']
            mobile = kwargs.get('mobile')
            mobile_trusted = kwargs.get('mobile_trusted')
            if (mobile is None
                and mobile_trusted is False
               ):
                # don't reset mobile_trusted if no new mobile is provided
                del kwargs['mobile_trusted']
            if (mobile is not None
                and mobile == user.mobile
                and mobile_trusted is False
               ):
                # don't reset mobile_trusted if there is no mobile number
                # change
                del kwargs['mobile_trusted']
            for k, v in kwargs.iteritems():
                setattr(user, k, v)
        else:
            user = User(email=email, **kwargs)
        user.store(refresh=True)
        return user

    def __repr__(self):
        return "<%s [id=%r, %r]>" % (self.__class__.__name__,
                                     self.id,
                                     self.email)


class SessionUser(object):
    """A user to be used for session users

    A `session user` is a user which is not authenticated but has a session
    authentication cookie assigned.

    This is used for unauthenticated access to identify a user without a
    login.
    """

    SESSION_USER_PREFIX = 'iris-session:'
    SYSRANDOM = random.SystemRandom()

    def __init__(self, id=None):
        if id is None:
            # create a random session user id
            id = (self.SESSION_USER_PREFIX +
                  str(self.SYSRANDOM.randint(0, 10000000000))
                 )
        self.id = id

    def get_roles(self):
        """"""
        return [acl.Roles.SessionUser]

    def set_roles(self, roles):
        pass

    roles = property(get_roles, set_roles)

    @classmethod
    def get(cls, id, **kwargs):
        """Returns an instance of SessionUser if id is a session user id
        """
        if id and id.startswith(cls.SESSION_USER_PREFIX):
            return cls(id)
        return None

    @classmethod
    def is_session_user_id(cls, id):
        return id.startswith(cls.SESSION_USER_PREFIX)

    @classmethod
    def is_session_user(cls, user):
        return isinstance(user, SessionUser)

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.id)


def get_user(user_id):
    """Get a user based on the user id

    If the user id represents a session user id a SessionUser instance is
    returned.
    """
    user = SessionUser(user_id)
    if user is None:
        user = User.get(user_id)
    return user
