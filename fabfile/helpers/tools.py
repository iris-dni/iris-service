from fabric.utils import abort
from fabric.colors import red

from elasticsearch import Elasticsearch

from ..consts import SETTINGS


def get_settings(env_name):
    """Check if env_name is a valid environment

    Print a message and abort if env_name is not known.
    """
    if env_name not in SETTINGS:
        print red('Unknown environment: "%s"' % env_name)
        print red('Use one of: "%s"' % ', '.join(SETTINGS.keys()))
        abort(red('Aborted!'))
    settings = SETTINGS[env_name]
    return settings


def get_es(settings):
    return Elasticsearch(settings.get('crate_host'))
