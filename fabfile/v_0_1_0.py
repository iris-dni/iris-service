from functools import partial

from fabric.api import execute, local

from .migrate import do_index
from .helpers import get_settings

from .migrate import addMigration


VERSION = (0, 1, 0)


def migrate(env_name):
    """Migration

    Upgrade these indices:
        - weblocations

    After the index migration the og properties of all weblocations are set to
    null to trigger a new open graph data update.

    Because of an index change which needs a full reindex the current index
    must be destroyed and recreated.

    Important:
        The index will be created based on the local sql definitions not the
        one which is deployed.

    Note:
        The index will be temporarily unavailable (step 3-4) or not all data is
        available (step 5).
    """
    settings = get_settings(env_name)
    execute(partial(do_index,
                    env_name,
                    "weblocations",
                   ), hosts=settings['hosts'])
    local(('curl -sSXPOST \'{crate_host}/_sql?pretty\''
           ' -d \'{{"stmt":"update weblocations set og = null"}}\''
          ).format(**settings))

addMigration(VERSION, migrate)
