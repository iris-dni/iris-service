import time
from elasticsearch import Elasticsearch, helpers


def copyIndex(from_es, from_idx, to_idx, to_es='', force_copy='0'):
    es_from = Elasticsearch(from_es)
    es_to = None
    if to_es:
        es_to = Elasticsearch(to_es)
    old_to_settings = None
    es_check = es_to or es_from
    to_exists = es_check.indices.exists(to_idx)
    if force_copy != '1' and to_exists:
        print
        print 'Error: Target index "%s" exists!' % to_idx
        print
        return
    if not to_exists:
        # create a destination index which is not indexing any data (speed)
        es_check.indices.create(
            to_idx,
            body={
                "settings": {
                    "number_of_shards": 5,
                    "number_of_replicas": 0,
                    "refresh": -1,
                },
                "mappings": {
                    "_default_": {
                        "dynamic": False,
                        "_all": {
                            "enabled": False
                        },
                    }
                }
            }
        )
    else:
        print 'Temporarily set number of replicas to 0...'
        old_to_settings = es_check.indices.get_settings(to_idx)
        es_check.indices.put_settings(
            body={
                "number_of_replicas": 0,
                "auto_expand_replicas": False,
            },
            index=to_idx,
        )
    start = time.time()
    result = helpers.reindex(es_from,
                             from_idx,
                             to_idx,
                             target_client=es_to,
                             chunk_size=500,
                             bulk_kwargs={
                                 "stats_only": False,
                                 "raise_on_error": False,
                             },
                            )
    duration = time.time() - start
    print
    if result[1]:
        print '========================================'
        print 'documents with errors:'
        for r in result[1]:
            print r
        print '========================================'
        print
    print ('copied:', result[0],
           'in', duration, 'sec,',
           result[0] / duration, 'docs/second')
    print
    if old_to_settings is not None:
        print 'Restoring replica settings...'
        index_settings = old_to_settings[to_idx]['settings']['index']
        es_check.indices.put_settings(
            body={
                "number_of_replicas": index_settings.get(
                                            'number_of_replicas',
                                            0),
                "auto_expand_replicas": index_settings.get(
                                            'auto_expand_replicas',
                                            False),
            },
            index=to_idx,
        )


if __name__ == '__main__':
    # this is used to run this script on the remote host
    import sys
    args = sys.argv[1:]
    while len(args) < 5:
        args.append('')
    copyIndex(from_es=args[0],
              from_idx=args[1],
              to_idx=args[2],
              to_es=args[3],
              force_copy=args[4])
