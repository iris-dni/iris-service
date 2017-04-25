from iris.service import twitter

from .mail import prepare_petition


def tweet_petition(request, template, petition):
    """Send a tweet for a petition
    """
    data = prepare_petition(request, petition)
    return twitter.send(template, data)
