import os
from fabric.api import run, sudo, env, task, put

import fabtools.python
import fabtools.rpm
import fabtools.files

env.forward_agent = True
env.user = 'admin'


TMP_VENV_DIR = '/tmp/copyIndex'
SRC_DIR = os.path.join(TMP_VENV_DIR, 'src')
REMOTE_PY = os.path.join(TMP_VENV_DIR, 'bin', 'python')

HERE = os.path.dirname(__file__)


@task
def copyIndex(from_es, from_idx, to_idx, to_es='', force_copy='0'):
    """Copy an elasticsearch index

    Allows to copy an index into a new index or other existing index.
    The copy can be inside an instance or between different instances.

    If a remote host is specified the copy code is executed on the remote
    machine.

    Arguments:
        from_es: origin elasticsearch host name
        from_idx: origin index name
        to_idx: target index name
        to_es: target elasticsearch host name
        force_copy: copy to target even if the target index exists
    """
    if env.host is not None:
        # run the code on the remote machine
        RemoteIndexCopy(from_es, from_idx, to_idx, to_es, force_copy)()
    else:
        LocalIndexCopy(from_es, from_idx, to_idx, to_es, force_copy)()


class IndexCopyBase(object):

    def __init__(self, from_es, from_idx, to_idx, to_es, force_copy):
        self.from_es = from_es
        self.from_idx = from_idx
        self.to_idx = to_idx
        self.to_es = to_es
        self.force_copy = force_copy

    def __call__(self):
        raise NotImplementedError


class LocalIndexCopy(IndexCopyBase):

    def __call__(self):
        from .helpers import es_copyindex
        es_copyindex.copyIndex(self.from_es,
                               self.from_idx,
                               self.to_idx,
                               self.to_es,
                               self.force_copy,
                              )


class RemoteIndexCopy(IndexCopyBase):

    def __call__(self):
        self.setupRemote()
        cmd = [os.path.join(SRC_DIR, 'copyindex.py'),
               self.from_es,
               self.from_idx,
               self.to_idx,
               self.to_es,
               self.force_copy
              ]
        run(REMOTE_PY + ' ' + ' '.join(['"%s"' % c for c in cmd]))
        self.shutdownRemote()

    def setupRemote(self):
        sudo('rm -rf ' + TMP_VENV_DIR)
        if not fabtools.rpm.is_installed('python-virtualenv'):
            fabtools.rpm.install('python-virtualenv')
        if not fabtools.python.virtualenv_exists(TMP_VENV_DIR):
            fabtools.python.create_virtualenv(
                TMP_VENV_DIR,
                venv_python='/opt/python-2.7/bin/python',
                )
        run('mkdir %s' % SRC_DIR)
        put(os.path.join(HERE, 'helpers/es_copyindex.py'),
            os.path.join(SRC_DIR, 'copyindex.py'),
        )
        with fabtools.python.virtualenv(TMP_VENV_DIR):
            fabtools.python.install('elasticsearch==1.9.0')

    def shutdownRemote(self):
        fabtools.files.remove(TMP_VENV_DIR, recursive=True)
