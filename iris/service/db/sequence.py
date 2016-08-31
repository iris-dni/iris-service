import short_url

from lovely.essequence import Sequence

# the shortener used to create the shortened ids
SHORT_ALPHABET = ('17HSkUENfxta3uqdgZGowKIBRDsOPzX'
                  + '9v8rnLb05VcA4pCyWljF6QJTihMme2Y'
                 )
SHORT = short_url.UrlEncoder(alphabet=SHORT_ALPHABET)


#====================================================================
#
# IID generator
#
# Here we define a central generator for iids used as primary keys for the
# database documents.
#
IID_NAME = 'iid'

# IID generator to be used if an integer id is needed
IID = Sequence(IID_NAME).next


def iid_unicode(iid):
    # we always return a unicode string
    return unicode(SHORT.encode_url(iid))

# IID generator to be used if a shorted string is needed as id
IID_SHORTED = Sequence(IID_NAME, transform=iid_unicode).next
