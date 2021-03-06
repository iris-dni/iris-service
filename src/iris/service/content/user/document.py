import random
from phonenumbers import (
    parse as pn_parse,
    format_number as pn_format_number,
    PhoneNumberFormat,
    NumberParseException,
)

from lovely.esdb.document import Document
from lovely.esdb.properties import Property

from iris.service.security import acl

from iris.service.db.dc import dc_defaults, DC_CREATED, DC_MODIFIED
from iris.service.db.sequence import IID_SHORTED


def obfuscate_phone_number(nr):
    """Obfuscate phone numbers for public use.

    Returns a string formatted as '+41 <a><b> XXX XX <y><z>'
    If there aren't enough numbers, 'XXX XX' is returned.
    """
    if not nr:
        return nr
    nr = nr.lstrip('0')
    if nr.startswith('+'):
        if len(nr) > 6:
            return '+' + nr[1:3] + ' ' + nr[3:5] + ' XXX XX ' + nr[-2:]
        return 'XXX XX'
    if len(nr) > 5:
        return '+' + nr[0:2] + ' ' + nr[2:4] + ' XXX XX ' + nr[-2:]
    return 'XXX XX'


def normalise_phone_number(nr):
    if not nr:
        return nr
    try:
        number = pn_parse(nr, 'CH')
        return pn_format_number(number, PhoneNumberFormat.E164)
    except NumberParseException:
        # Apparently, not all numbers are valid.
        # e.g. 'faker' (used in sample data) produces phone numbers such as
        # u'+08(2)9338238082'. In such cases, we try our own version:
        nr = nr.replace('(', '').replace(')', '').replace(' ', '')
        if nr.startswith('+'):
            return nr
        if nr.startswith('00'):
            return nr.replace('00', '+', 1)
        raise ValueError("Invalid number")


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

    @mobile.setter
    def set_mobile(self, value):
        return normalise_phone_number(value)

    mobile_trusted = Property(
        default=False
    )

    salutation = Property(default='')
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
            mobile = normalise_phone_number(kwargs.get('mobile'))
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
