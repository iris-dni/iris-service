from functools import partial

from fabric.api import execute, local

from .migrate import do_index
from .helpers import get_settings

from .migrate import addMigration


VERSION = (0, 1, 1)


def migrate(env_name):
    """Migration

    Upgrade these indices:
        - petitions

    After the index migration the city_answer properties of all petitions is
    reset to the default values.

    Because of an index change which needs a full reindex the current index
    must be destroyed and recreated.

    Important:
        The index will be created based on the local sql definitions not the
        one which is deployed.
    """
    settings = get_settings(env_name)
    local(('curl -sSXPOST \'{crate_host}/_sql?pretty\''
           ' -d \'{{"stmt":"update petitions set city_answer = null"}}\''
          ).format(**settings))
    execute(partial(do_index,
                    env_name,
                    "petitions",
                   ), hosts=settings['hosts'])
    local(('curl -sSXPOST \'{crate_host}/_sql?pretty\''
           ' -d \'{{"stmt":"update petitions set city_answer = {{}}"}}\''
          ).format(**settings))
    local(('curl -sSXPOST \'{crate_host}/_sql?pretty\''
           ' -d \'{{"stmt":"update petitions'
           '                       set city_answer[\'\\\'\'text\'\\\'\']'
           '                           = \'\\\'\'\'\\\'\'"}}\''
          ).format(**settings))
    local(('curl -sSXPOST \'{crate_host}/_sql?pretty\''
           ' -d \'{{"stmt":"update petitions'
           '                       set city_answer[\'\\\'\'name\'\\\'\']'
           '                           = \'\\\'\'\'\\\'\'"}}\''
          ).format(**settings))

addMigration(VERSION, migrate)
