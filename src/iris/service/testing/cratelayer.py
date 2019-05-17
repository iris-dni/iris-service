import os.path
import requests

from . import project_path, testing_path
from .dockerlayer import DOCKER_LAYER
from argparse import Namespace
from iris.service.scripts.setup_db import execute_sql_files
from lovely.essequence import sequence

crate_setup_dir = project_path('etc', 'sql')
setup_db_settings = testing_path('sql.py')


class CrateLayer(object):
    __bases__ = ()

    def __init__(self, docker_layer):
        self.__name__ = "crate"
        self.docker_layer = docker_layer
        self.authority = None

    def setUp(self):
        host, port = self.docker_layer.start_http_service(self.__name__, 4200)
        self.authority = "%s:%s" % (host, port)
        # allow dirty startup

    def testSetUp(self):
        self.delete_crate_indexes()
        self.create_crate_indexes()

    def testTearDown(self):
        self.delete_crate_indexes()
        sequence.testing_reset_sequences()

    def delete_crate_indexes(self):
        """Deletes the Crate indexes.
        """
        url = "http://%s/_aliases" % self.authority
        for index in requests.get(url).json().keys():
            url = "http://%s/%s" % (self.authority, index)
            requests.delete(url)
        self.wait_for_cluster()

    def create_crate_indexes(self):
        """Creates the Crate indexes defined in etc/sql/sql.sql
        """
        sql_file = os.path.join(crate_setup_dir, 'sql.sql')
        execute_sql_files(Namespace(
            host=self.authority,
            settings=setup_db_settings,
            files=[sql_file]
        ))
        self.wait_for_cluster()

    def wait_for_cluster(self):
        healthurl = 'http://%s/_cluster/health' % self.authority
        params = {'wait_for_status': 'green',
                  'timeout': '300s'}
        res = requests.get(healthurl, params=params)
        assert res.status_code == 200
        health = res.json()
        assert health['status'] != 'red'


CRATE_LAYER = CrateLayer(DOCKER_LAYER)