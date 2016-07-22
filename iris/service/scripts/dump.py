import json
import sys

from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan


def dump(argv=None, outfile=None):
    """Dump the indices of a crate cluster to standard out. The first param
    filters for a specific index. Use 'all' to dump all indexes
    (default value). The second param is the crate host to dump from.
    """
    args = (argv or sys.argv)[1:]
    if len(args) < 1:
        print 'need at least HOST as parameter'
        return 1
    host = args[-1]
    es = Elasticsearch(host)
    state = es.cluster.state()
    indexes = state['metadata']['indices'].iterkeys()
    index = 'all'
    if len(args) > 1:
        index = args[1].lower()
    for index_name in indexes:
        if index == 'all' or index == index_name:
            _scan_index(index_name, es, outfile)


def _scan_index(index_name, es, outfile):
    for row in scan(es,
                    {'query': {'match_all': {}}},
                    scroll='1m',
                    index=index_name,
                    size=1000,
                    ):
        data = row.get('_source', {})
        index = {'_index': row['_index'],
                 '_type': row['_type'],
                 '_id': row['_id'],
                 }
        if outfile is not None:
            outfile.write(json.dumps({'index': index}) + '\n')
            outfile.write(json.dumps(data) + '\n')
        else:
            print json.dumps({'index': index})
            print json.dumps(data)
