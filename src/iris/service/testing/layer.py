import os.path
import requests

from crate.testing.layer import CrateLayer
from lovely.testlayers.layer import CascadedLayer


here = os.path.dirname(os.path.dirname(__file__))
buildout_dir = os.path.dirname(os.path.dirname(here))


def crate_path(*parts):
    return os.path.join(buildout_dir, 'parts', 'crate', *parts)

crate_port = 19342
crate_host = '127.0.0.1:%s' % crate_port
crate_settings = os.path.join(here, 'testing', 'crate.yml')
crate_setup_dir = os.path.join(buildout_dir, 'etc', 'sql')
crash_path = os.path.join(buildout_dir, 'bin', 'crash')
setup_db_path = os.path.join(buildout_dir, 'bin', 'setup_db')
setup_db_settings = os.path.join(here, 'testing', 'sql.py')
crate_cleanup = os.path.join(buildout_dir, 'bin', 'crate_cleanup')
crate_setup = os.path.join(buildout_dir, 'bin', 'crate_setup')

crate_layer = CrateLayer('crate',
                         crate_home=crate_path(),
                         crate_config=crate_settings,
                         crate_exec=crate_path('bin', 'crate'),
                         port=crate_port)

crateDBLayer = CascadedLayer('crateDBLayer', crate_layer)

crate2_layer = CrateLayer('crate2',
                          crate_home=crate_path(),
                          crate_config=crate_settings,
                          crate_exec=crate_path('bin', 'crate'),
                          port=crate_port)
crate2DBLayer = CascadedLayer('crate2DBLayer', crate2_layer)


def delete_crate_indexes():
    """Deletes the Crate indexes.
    """
    url = "http://%s/_aliases" % crate_host
    for index in requests.get(url).json().keys():
        url = "http://%s/%s" % (crate_host, index)
        requests.delete(url)
    wait_for_cluster()


def create_crate_indexes():
    """Creates the Crate indexes defined in etc/sql/sql.sql
    """
    sql_file = os.path.join(crate_setup_dir, 'sql.sql')
    cmd = "%s --crash %s --host %s --settings %s %s" % (
        setup_db_path, crash_path, crate_host, setup_db_settings, sql_file)
    os.system(cmd)
    wait_for_cluster()


def wait_for_cluster():
    healthurl = 'http://%s/_cluster/health' % crate_host
    params = {'wait_for_status': 'green',
              'timeout': '300s'}
    res = requests.get(healthurl, params=params)
    assert res.status_code == 200
    health = res.json()
    assert health['status'] != 'red'
