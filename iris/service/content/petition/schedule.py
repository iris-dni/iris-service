import logging

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
        petitions = Petition.search(
            {
                "query": {
                    "term": {
                        "state.tick": True
                    }
                }
            }
        )
        for petition in petitions['hits']['hits']:
            logging.info('Sending tick to petition "%s"' % petition.id)
            if petition.sm(None).tick():
                petition.store()
