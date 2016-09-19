import time

from elasticsearch import exceptions

from fabric.colors import red

from .tools import get_es


class PersistentVersion(object):
    """Manage the persistent version in the database
    """

    def __init__(self, settings, tag):
        self.settings = settings
        self.tag = tag

    def get_version(self):
        es = get_es(self.settings)
        try:
            result = es.get(index='versions', doc_type='default', id=self.tag)
            return result['_source']['version']
        except exceptions.NotFoundError:
            return '0.0.0'

    def set_version(self, value):
        es = get_es(self.settings)
        try:
            es.index(index='versions',
                     doc_type='default',
                     id=self.tag,
                     body={
                         "id": self.tag,
                         "version": value,
                         "updated": int(time.time() * 1000)
                     })
        except exceptions.NotFoundError:
            print red('Can not set version: index missing ')

    version = property(get_version, set_version)
