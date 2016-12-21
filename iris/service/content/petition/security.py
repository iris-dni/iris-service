import base64
import hashlib
import hmac
import time


PETITION_SECRET_KEY = None


def generate_petition_token(petition):
    """
    Generate a token for a given petition.
    It encodes the petition's ID and the current timestamp
    """
    token = _generate_signature(petition.id, int(time.time()))
    return base64.b64encode(token)


def verify_petition_token(request):
    """
    Verify the token for given request.

    A 'token' and a 'petition' must be present in the `request`.

    Implementation note:
        - we decode the token (base64) -> '{token},{timestamp}'
        - we extract the timestamp
        - we generate the same token with extracted timestamp and given
          petition ID.
        - if the generated token matches with '{token}', it's considered
          verified.
    """
    if not request:
        return False
    challengerToken = request.swagger_data.get('token', '')
    petitionId = request.swagger_data.get('petition', '')
    try:
        sig, timestamp = base64.b64decode(challengerToken).split(',')
        token = _generate_signature(petitionId, timestamp)
        if base64.b64encode(token) == challengerToken:
            return True
        return False
    except (TypeError, ValueError):
        return False


def _generate_signature(petitionId, timestamp):
    sig = hmac.new(PETITION_SECRET_KEY,
                   u'petition-{id} {ts}'.format(id=petitionId, ts=timestamp),
                   hashlib.sha1).hexdigest()
    return u'{sig},{ts}'.format(sig=sig, ts=timestamp)


def includeme(config):
    global PETITION_SECRET_KEY
    settings = config.get_settings()
    PETITION_SECRET_KEY = settings.get('iris.secret.petition')
