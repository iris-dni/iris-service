import logging

from iris.service import twitter

from .mail import prepare_petition

log = logging.getLogger(__name__)


def tweet_petition(request, template, petition):
    """Send a tweet for a petition
    """
    if request is None:
        # this happens in tests when creating random sampledata
        return None
    data = prepare_petition(request, petition)
    try:
        return twitter.send(template, data)
    except twitter.TwitterError as e:
        log.error(e.message)
        return None
