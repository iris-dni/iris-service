import hashlib
import time

from lovely.esdb.document import Document
from lovely.esdb.properties import Property
from lovely.essequence import Sequence

from ..db.dc import dc_defaults, DC_CREATED


# IID generator for the token ids
IID = Sequence('ssotokens').next


SSO_TOKEN_LIFETIME = 60  # seconds


def token_generator():
    return hashlib.md5('__ssotokens__' + str(IID())).hexdigest()


class SSOToken(Document):

    INDEX = 'ssotokens'

    token = Property(
        primary_key=True,
        default=token_generator,
        doc="The token Id"
    )

    dc = Property(
        default=dc_defaults(DC_CREATED),
        doc="Dublin Core data."
    )

    sso = Property(
        doc="The sso message"
    )

    apikey = Property(
        doc="The apikey which belongs to the sso property"
    )

    @classmethod
    def resolve(cls, token):
        """Resolve the token into a tuple (sso, apikey)

        Returns None if the token could not be found.
        The database entry for the token is deleted.
        """
        ssotoken = cls.get(token)
        if ssotoken is None:
            return None
        expire_time = int(time.time()) - SSO_TOKEN_LIFETIME
        if ssotoken.dc.get('created', 0) < expire_time:
            # expired
            return None
        result = (ssotoken.sso, ssotoken.apikey)
        ssotoken.delete(refresh=True)
        return result

    def __repr__(self):
        return "<%s [token=%r]>" % (self.__class__.__name__,
                                    self.token)
