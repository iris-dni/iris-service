import logging
from elasticsearch import helpers

from iris.service.rest import blank_request
from iris.service.elector import Elector

from .document import Petition


logger = logging.getLogger(__name__)

PETITION_ELECTOR = Elector('petition')


class TickWorker(object):
    """A worker to update the petition states.

    Send a tick event to all petitions where state.tick is True.
    """

    def __call__(self):
        logging.info('Running petition tick worker')
        query = {
            "query": {
                "term": {
                    "state.tick": True
                }
            }
        }
        for result in helpers.scan(Petition.ES,
                                   query=query,
                                   index=Petition.INDEX,
                                   doc_type=Petition.DOC_TYPE,
                                  ):
            petition = Petition.from_raw_es_data(result)
            logging.info('Sending tick to petition "%s"' % petition.id)
            request = blank_request()
            if petition.sm(request).tick():
                petition.store()
