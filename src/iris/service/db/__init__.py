from pyramid.settings import aslist

from elasticsearch import Elasticsearch

from lovely.esdb.document import Document
from lovely.essequence import Sequence

ES = None


def get_es():
    return ES


def includeme(config):
    """Setup database related globals
    """
    settings = config.get_settings()
    # setup a global Elasticsearch instance
    global ES
    es_settings = {}
    for key, value in settings.iteritems():
        if key.startswith('es.'):
            es_settings[key[3:]] = value
    hosts = aslist(es_settings.pop('hosts'))
    ES = Elasticsearch(hosts, **es_settings)
    # use the global Elasticsearch instance for all documents
    Document.ES = ES
    # use the global Elasticsearch instance for all sequences
    Sequence.ES = ES
