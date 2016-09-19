import os
from fabric.api import run, sudo, env, task, put, cd

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

    REMOTE_TMP = 'tmp/iris'

    def __call__(self):
        self.setupRemote()
        cmd = ['sudo',
               'docker',
               'run',
               '-ti',
               '--rm',
               'iris-migration',
               'python',
               'es_copyindex.py',
               self.from_es,
               self.from_idx,
               self.to_idx,
               self.to_es,
               self.force_copy
              ]
        cmd = ' '.join(['"%s"' % c for c in cmd])
        run(cmd)
        self.shutdownRemote()

    def setupRemote(self):
        run('mkdir -p ' + self.REMOTE_TMP)
        put('fabfile/helpers/es_copyindex.py', self.REMOTE_TMP)
        put('fabfile/Dockerfile', self.REMOTE_TMP)
        with cd(os.path.join(self.REMOTE_TMP)):
            run('sudo docker build -t iris-migration .')

    def shutdownRemote(self):
        run('rm -rf ' + self.REMOTE_TMP)
