from copy import deepcopy
from elasticsearch import Elasticsearch

from .helpers import get_settings

from .migrate import addMigration

from iris.service.content.user import User, normalise_phone_number
from iris.service.content.petition.document import Petition, Supporter
from iris.service.content.confirmation import Confirmation

from fabric.colors import red, green


VERSION = (0, 2, 0)

ES = None


def get_es(settings):
    global ES
    if not ES:
        host = '{crate_host}'.format(**settings)
        ES = Elasticsearch(host)
    return ES


def migrate_users(settings):
    User.ES = get_es(settings)
    users = User.search({
        "query": {
            "filtered": {
                "filter": {
                    "bool": {
                        "must": [
                            {"exists": {"field": "mobile"}},
                            {"not": {"term": {"mobile": ""}}}
                        ]
                    }
                }
            }
        },
        "sort": {"dc.created": {"order": "asc"}},
        "size": 20000
    })['hits']['hits']
    for user in users:
        try:
            old = user.mobile
            if old:
                new = normalise_phone_number(old)
                print green(
                    "Migrating user ('{id}') from '{old}' to '{new}'".format(
                        id=user.id,
                        old=old,
                        new=new,
                    ))
                user.mobile = new
                user.store()
            else:
                print green("Skipping migration for user '{id}'. "
                            "No 'user.mobile' available".format(id=user.id))
        except ValueError:
            print red("Could not migrate user with id '{id}'".format(
                      id=user.id))


def migrate_petitions(settings):
    Petition.ES = get_es(settings)
    petitions = Petition.search({
        "query": {
            "filtered": {
                "filter": {
                    "bool": {
                        "must": [
                            {"exists": {"field": "relations.owner.mobile"}},
                            {"not": {"term": {"relations.owner.mobile": ""}}}
                        ]
                    }
                }
            }
        },
        "sort": {"dc.created": {"order": "asc"}},
        "size": 20000
    })['hits']['hits']
    for petition in petitions:
        try:
            old = petition.owner.relation_dict['mobile']
            if old:
                new = normalise_phone_number(old)
                print green(
                    "Migrating petition ('{id}') from '{old}' to '{new}'".format(
                        id=petition.id,
                        old=old,
                        new=new,
                    ))
                newOwner = deepcopy(petition.owner.relation_dict)
                newOwner['mobile'] = new
                petition.owner = newOwner
                petition.store()
            else:
                print green("Skipping migration for petition '{id}'. "
                            "No 'petition.owner.mobile' "
                            "available".format(id=petition.id))
        except ValueError:
            print red("Could not migrate petition with id '{id}'".format(
                      id=petition.id))


def migrate_supporters(settings):
    Supporter.ES = get_es(settings)
    supporters = Supporter.search({
        "query": {
            "filtered": {
                "filter": {
                    "bool": {
                        "must": [
                            {"exists": {"field": "relations.user.mobile"}},
                            {"not": {"term": {"relations.user.mobile": ""}}}
                        ]
                    }
                }
            }
        },
        "sort": {"dc.created": {"order": "asc"}},
        "size": 20000
    })['hits']['hits']
    for supporter in supporters:
        try:
            old = supporter.user.relation_dict['mobile']
            if old:
                new = normalise_phone_number(old)
                print green(
                    "Migrating supporter ('{id}') from '{old}' to "
                    "'{new}'".format(
                        id=supporter.id,
                        old=old,
                        new=new,
                    ))
                newUser = deepcopy(supporter.user.relation_dict)
                newUser['mobile'] = new
                supporter.user = newUser
                supporter.store()
            else:
                print green("Skipping migration for supporter '{id}'. "
                            "No 'mobile' available".format(id=supporter.id))
        except ValueError:
            print red("Could not migrate supporter with id '{id}'".format(
                      id=supporter.id))


def migrate_confirmations(settings):
    Confirmation.ES = get_es(settings)
    # fetch all confirmations which are either handle by 'petition_sms' or
    # 'support_sms'.
    confirmations = Confirmation.search({
        "query": {
            "filtered": {
                "filter": {
                    "bool": {
                        "should": [
                            {"term": {"handler": "petition_sms"}},
                            {"term": {"handler": "support_sms"}}
                        ]
                    }
                }
            }
        },
        "sort": {"dc.created": {"order": "asc"}},
        "size": 20000
    })['hits']['hits']
    for confirmation in confirmations:
        try:
            if confirmation.handler == 'petition_sms':
                old = confirmation.data.get('mobile')
                if old:
                    new = normalise_phone_number(old)
                    print green(
                        "Migrating confirmation ('{id}': 'petition_sms') from "
                        "'{old}' to '{new}'".format(
                            id=confirmation.id,
                            old=old,
                            new=new,
                        ))
                    confirmation.data['mobile'] = new
                    confirmation.store()
                else:
                    print green("Skipping migration for confirmation "
                                "('{id}': 'petition_sms'). No 'data.mobile' "
                                "available".formatt(id=confirmation.id))
            if confirmation.handler == 'support_sms':
                old = confirmation.data.get('user', {}).get('mobile')
                if old:
                    new = normalise_phone_number(old)
                    print green(
                        "Migrating confirmation ('{id}': 'support_sms') from "
                        "'{old}' to '{new}'".format(
                            id=confirmation.id,
                            old=old,
                            new=new,
                        ))
                    confirmation.data['user']['mobile'] = new
                    confirmation.store()
                else:
                    print green("Skipping migration for confirmation "
                                "('{id}': 'support_sms'). No "
                                "'data.user.mobile' available".formatt(
                                                        id=confirmation.id))
        except ValueError:
            print red("Could not migrate confirmation with id '{id}'".format(
                      id=confirmation.id))


def migrate(env_name):
    """Migration

    Upgrade these indices:
        - Users (user.mobile)
        - Supporters (supporter.relations.user.mobile)
        - Petitions (petition.relations.owner.mobile)
        - Confirmations (handler 'petition_sms': confirmation.data.mobile
                         handler 'support_sms': confirmation.data.user.mobile)

    After the index migrations the 'mobile' fields of all documents are
    "normalised".
    """
    settings = get_settings(env_name)
    migrate_users(settings)
    migrate_petitions(settings)
    migrate_supporters(settings)
    migrate_confirmations(settings)


addMigration(VERSION, migrate)
