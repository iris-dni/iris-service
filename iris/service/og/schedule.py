import time
import logging
from gevent import Greenlet
import requests
import elasticsearch

from iris.service.elector import Elector
from iris.service.content.weblocation import WebLocation

from .og import OGDataRequester


logger = logging.getLogger(__name__)

OG_ELECTOR = Elector('og')


class Worker(Greenlet):
    """A worker to update og information for weblocations

    The worker uses an elector to coordinate its work with other running iris
    service instances.
    """

    def run(self):
        time.sleep(10)
        while True:
            if OG_ELECTOR.is_elected:
                try:
                    self.do_og_update()
                except (Exception,
                        elasticsearch.ElasticsearchException
                       ) as e:
                    logging.error('do_og_update raised exception "%s"', e)
                time.sleep(4)
            else:
                time.sleep(15)

    def do_og_update(self):
        """Update og data for all weblocations where og is None
        """
        count = 0
        query = {
            "query": {
                "filtered": {
                    "filter": {
                        "not": {
                            "exists": {"field": "og"}
                        }
                    }
                }
            }
        }
        for loc in WebLocation.search(query)['hits']['hits']:
            try:
                data = OGDataRequester(loc.url)
            except requests.exceptions.RequestException:
                logging.error('Can not update OG data for "%s"' % loc.url)
                data = {}
            count += 1
            data = dict(**data)
            data['ts'] = int(time.time() * 1000)
            loc.og = data
            loc.store()
        if count:
            WebLocation.refresh()
        return count
