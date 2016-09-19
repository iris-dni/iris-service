from functools import partial

from fabric.api import execute, task, prompt, local, env
from fabric.utils import abort
from fabric.colors import red, green, yellow

from .helpers.persistentversion import PersistentVersion
from .helpers import get_settings, get_es


MIGRATIONS = {}


def addMigration(version, handler):
    MIGRATIONS[version] = handler


@task
def auto(env_name):
    """Auto migration based on the entry in the versions table.

    """
    settings = get_settings(env_name)
    setup_db(settings)
    version = PersistentVersion(settings, 'service')
    migrated = True
    while migrated:
        migrated = False
        v = tuple([int(i) for i in version.version.split('.')])
        for mv in sorted(MIGRATIONS.keys()):
            if mv > v:
                version_str = '.'.join([str(i) for i in mv])
                migration = MIGRATIONS[mv]
                print migration.__doc__
                print red('You are about to migrate from '
                          'version %s to version %s!' % (
                              version.version, version_str)
                         )
                result = prompt("Run migration (y/N)?")
                if not result.lower().startswith('y'):
                    abort(red('Migration aborted by user request!'))
                execute(partial(migration, env_name), hosts=settings['hosts'])
                # update the version in the database
                version.version = version_str
                migrated = True
                break


@task
def index(env_name, *args):
    """Migrate a single index

    Upgrade an index to a new index schema.

    This script will do:
        1) copy current index into a temporary index
        2) drop existing index
        3) recreate index with new structure
        4) copy temporary index back

    Important:
        The index will be created based on the local sql definitions not the
        one which is deployed.

    If something goes wrong:
        After the migration an index with the name tmp_<index> is left. If
        something goes wrong while recreating the original index, this is the
        copy of the index when the migration was started.

    Note:
        The index will be temporarily unavailable (step 2-3) or not all data is
        available (step 4).
    """
    if not args:
        abort(red('No index names provided!'))
    settings = get_settings(env_name)
    print index.__doc__
    print red('You are about to run the migration for')
    for arg in args:
        print red(' - %s' % arg)
    result = prompt("Run migration (y/N)?")
    if not result.lower().startswith('y'):
        abort(red('Migration aborted by user request!'))
    execute(partial(do_index, env_name, *args), hosts=settings['hosts'])


def do_index(env_name, *args):
    settings = get_settings(env_name)

    def do_migrate(index_name):
        """Processes the migration for an index
        """
        reliable_index_copy(index_name,
                            'tmp_' + index_name,
                            False,
                            settings)
        es = get_es(settings)
        print green('Index "{index_name}" '
                    'copied to "tmp_{index_name}"'.format(
                                            index_name=index_name))
        print red('dropping index "{index_name}"'.format(
                                            index_name=index_name))
        es.indices.delete(index_name)
        print yellow('recreating dropped index "{index_name}"'.format(
                                            index_name=index_name))
        setup_db(settings)
        reliable_index_copy('tmp_' + index_name,
                            index_name,
                            True,
                            settings)

    print
    for arg in args:
        print green('======================================='
                    '=======================================')
        print
        print 'Starting migration for index "%s"' % arg
        execute(partial(do_migrate, arg), hosts=settings['hosts'])
        print
        print green('======================================='
                    '=======================================')
    print


def setup_db(settings):
    local('bin/setup_db --setting etc/{sql_settings}.py'
          '             --host {crate_host}'
          '             etc/sql/sql.sql'.format(**settings))


def reliable_index_copy(from_, to, force_write, settings):
    if not force_write:
        # drop the target index
        es = get_es(settings)
        es.indices.delete(to, ignore=[400, 404])
    ext = ''
    if force_write:
        ext = ',,1'
    host = ''
    if env.host_string != 'localhost':
        host = '-H ' + env.host_string
    local(('bin/fab {host} es.copyIndex:'
           '{crate_host},{from_},{to}{ext}'
          ).format(host=host,
                   from_=from_,
                   to=to,
                   ext=ext,
                   **settings
                  )
    )
