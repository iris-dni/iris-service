import time
import transitions

from transitions.extensions.nesting import NestedState

from iris.service.security import acl
from iris.service import rest
from iris.service.rest import queries
from iris.service.rest.extender import APIExtender

from iris.service.content.user import SessionUser, normalise_phone_number
from iris.service.content.city import City

from .sm import PetitionStateMachine, fromYAML
from .document import Petition, Supporter

PETITIONS_MAPPER_NAME = 'petitions'
PETITIONS_PUBLIC_MAPPER_NAME = 'petitions_public'


def stateFilter(value):
    if isinstance(value, (list, tuple)):
        states = [v.strip() for v in value if v.strip()]
    else:
        states = [v.lower().strip() for v in value.split(',') if v.strip()]
    if not states:
        raise ValueError("No states provided")
    filters = []
    for state in states:
        parts = state.split(NestedState.separator, 1)
        if len(parts) > 1:
            parent, name = parts
            if not name or name == '*':
                filters.append(queries.termFilter('state.parent')(parent))
            else:
                filters.append({
                    "bool": {
                        "must": [
                            queries.termFilter('state.name')(name),
                            queries.termFilter('state.parent')(parent)
                        ]
                    }
                })
        else:
            filters.append(queries.termFilter('state.name')(parts[0]))
    if len(filters) == 1:
        return filters[0]
    return {
        "bool": {
            "should": filters
        }
    }


def cityFilter(cityProperty):
    """
    city properties is either 'city.portal' or 'city.tags'
    """
    def wrapper(value):
        cities = City.search({
            "query": {
                "filtered": {
                    "filter": {
                        "bool": {
                            "must": queries.termsFilter(cityProperty)(value)
                        }
                    }
                }
            },
            "fields": []
        }, resolve_hits=False)['hits']['hits']
        cityIds = [c['_id'] for c in cities]
        return {"terms": {"relations.city": cityIds}}
    return wrapper


class PetitionsRESTMapper(rest.DocumentRESTMapperMixin,
                          rest.SearchableDocumentRESTMapperMixin,
                          rest.RESTMapper):
    """A mapper for the petitions REST API
    """

    NAME = PETITIONS_MAPPER_NAME

    DOC_CLASS = Petition

    QUERY_PARAMS = {
        'created_range': queries.rangeFilter('dc.created'),
        'ft': queries.fulltextQuery(['tags_ft',
                                     'title_ft',
                                     'description_ft',
                                     'suggested_solution_ft',
                                    ]),
        'tags_ft': queries.fulltextQuery(['tags_ft']),
        'title_ft': queries.fulltextQuery(['title_ft']),
        'description_ft': queries.fulltextQuery(['description_ft']),
        'suggested_solution_ft': queries.fulltextQuery(
            ['suggested_solution_ft']
        ),
    }

    FILTER_PARAMS = {
        'state': stateFilter,
        'tags': queries.termsFilter('tags'),
        'city': queries.termsFilter('relations.city'),
        'city.portal.id': cityFilter('portal.id'),
        'city.tags': cityFilter('tags'),
        'owner': queries.termsFilter('relations.owner.id'),
    }

    SORT_PARAMS = {
        'created': queries.fieldSorter('dc.created'),
        'modified': queries.fieldSorter('dc.modified'),
        'id': queries.fieldSorter('id'),
        'state': queries.fieldSorter('state.name'),
        'state.parent': queries.fieldSorter('state.parent'),
        'supporters.amount': queries.fieldSorter('supporters.amount'),
        'score': queries.scoreSorter,
        'default': queries.fieldSorter('dc.created', 'DESC'),
    }

    TRENDING_STEP_START = 7  # days
    TRENDING_STEP_MAX = 12 * 7

    def event(self, contentId, transitionName, data={},
              resolve=[], extend=[]):
        petition = Petition.get(contentId)
        if petition is None:
            return None
        sm = PetitionStateMachine(petition, self.request)
        transition_fn = getattr(sm, transitionName)
        if transition_fn is None:
            # transition doesn't exist
            raise transitions.MachineError(
                'Unknown transition "%s"' % transitionName)
        done = transition_fn(**data)
        if done:
            petition.store(refresh=True)
        return self.to_api(petition, resolve, extend)

    def statemachine(self):
        return fromYAML(raw=True)

    def get_by_token(self, token, resolve=[], extend=[]):
        doc = None
        found = self.DOC_CLASS.get_by(Petition.response_token, token)
        if found:
            doc = found[0]
        return self.to_api(doc, resolve, extend)

    def _prepare_data(self, doc, data):
        """Prepare API POST data for a petition

        The owner of the petition is set based on the current user from the
        request. This can also be a session user. An already set owner will be
        changed.
        """
        data_owner = data.get('owner', {})
        if doc is None:
            # New document, set the owner id to the currently logged in user
            owner = data.setdefault('owner', {})
            owner['id'] = self.request.session_user.id
        elif (data_owner.get('id') is None
              and (doc.owner.id is None
                   or SessionUser.is_session_user_id(doc.owner.id)
                  )
             ):
            # Existing document and no owner or owner is a session user.
            # Force the owner to the currently logged in user.
            doc.owner = self.request.session_user.id
        # manage the trusted flags if this is a change of an existing petition
        if doc is not None:
            # Check if the trusted flags on the relations are different
            # and reset the trusted flag is so.
            owner_rel = doc.owner.relation_dict
            if owner_rel.get('mobile') != normalise_phone_number(
                                                    data_owner.get('mobile')):
                data_owner['mobile_trusted'] = False
            if owner_rel.get('email') != data_owner.get('email'):
                data_owner['email_trusted'] = False

    def _prepare_document(self, doc, data, is_create):
        """Prepare the document before it is stored

        Manage the trusted flags.
        """
        owner = doc.owner()
        if owner is None:
            # No owner or a session owner, flags are already set in
            # _prepare_data.
            return
        owner_rel = doc.owner.relation_dict
        if (normalise_phone_number(owner_rel['mobile']) == owner.mobile
            and owner.mobile_trusted
           ):
            # The owners mobile is trusted so we can also trust the mobile
            # on the relation.
            doc.owner = {'mobile_trusted': True}
        if (owner_rel['email'] == owner.email
            and owner.email_trusted
           ):
            # The owners email is trusted so we can also trust the email
            # on the relation.
            doc.owner = {'email_trusted': True}

    DEFAULT_TRENDING = (7,   # look back days
                        90,  # max look back days
                        7    # increment
                       )

    def search(self,
               offset=0,
               limit=10,
               sort=None,
               testing_only=False,
               debug=None,
               trending=None,
               **params):
        """Extends the search endpoint with the special `trending` sort.

        It is possible to provide `sort=trending` which will then
        sort by trending petitions.
        If this sort is used all parameters except the `limit` are ignored.

        Trending petitions is implemented by searching for petitions with the
        most supports in the last `look back days` (see DEFAULT_TRENDING).
        If the query provides less than `limit` petitions the time range is
        extended by `increment`. This is repeated until `max look back days`
        is reached.

        For testing it is also possible to provide the trending parameters as
        `trending` query parameter. The parameter must provide a list with
        exactly 3 integer values. The values are used the same way as
        DEFAULT_TRENDING is defined.
        Example: trending=14,120,14
        """
        if (trending is None
            and (sort is None
                 or 'trending' not in sort)
           ):
            # use the standard search
            return super(PetitionsRESTMapper, self).search(
                offset, limit, sort, testing_only, debug, **params)
        if trending is None:
            # provide trending because of the sort
            trending = self.DEFAULT_TRENDING
        try:
            current, tr_max, tr_step = trending
        except:
            raise ValueError(
                'Wrong number (expected 3)'
                ' of parameters in trending: "%s"' % trending)
        first = True
        while True:
            if not first:
                current += tr_step
                if current > tr_max:
                    # don't go above the requested days
                    current = tr_max
                # next time use a bigger step
                tr_step *= 2
            first = False
            fromTs = (int(time.time()) - 86400 * current) * 1000
            query = queries.rangeFilter('dc.created', ['gte'])([fromTs])
            aggregations = {
                "trending": {
                    "terms": {
                        "field": "relations.petition",
                        "size": limit
                    }
                }
            }
            body = {
                "from": 0,
                "size": 0,
                "query": query,
                "aggregations": aggregations,
            }
            searchresult = Supporter.search(body)
            buckets = searchresult['aggregations']['trending']['buckets']
            if tr_step > 0 and current < tr_max and len(buckets) < limit:
                # not enough results
                continue
            data = []
            keys = [b['key'] for b in buckets[:limit]]
            if keys:
                data = self.listable_get(keys)
            if tr_step > 0 and current < tr_max and len(data) < limit:
                # not enough results
                continue
            result = {
                'data': self.to_api(data),
                'total': len(data),
            }
            return result

    def listable_get(self, ids):
        """Get only listable petitions by id
        """
        query = {
            "filtered": {
                "filter": {
                    "bool": {
                        "must": queries.termFilter('state.listable')(True)
                    }
                },
                "query": {
                    "bool": {
                        "must": queries.termsFilter('id')(ids)
                    }
                }
            }
        }
        body = {
            "from": 0,
            "size": len(ids),
            "query": query,
        }
        searchresult = Petition.search(body)
        return searchresult['hits']['hits']


class PetitionsPublicRESTMapper(PetitionsRESTMapper):
    """A mapper for the petitions public REST API

    Adds a filter which makes sure only `listable` petitions are provided.
    """

    NAME = PETITIONS_PUBLIC_MAPPER_NAME

    def _extend_filter(self, filters):
        filters.append(queries.termFilter('state.listable')(True))


class SupportersRESTMapper(rest.DocumentRESTMapperMixin,
                           rest.SearchableDocumentRESTMapperMixin,
                           rest.RESTMapper):
    """A mapper for the supporters admin REST API
    """

    NAME = 'supporters'

    DOC_CLASS = Supporter

    QUERY_PARAMS = {
    }

    FILTER_PARAMS = {
        'petition': queries.termsFilter('relations.petition'),
        'user': queries.termsFilter('relations.user.id'),
    }

    SORT_PARAMS = {
        'created': queries.fieldSorter('dc.created'),
        'id': queries.fieldSorter('id'),
        'default': queries.fieldSorter('dc.created', 'DESC'),
    }


class PetitionExtender(object):
    """Makes sure that private data is filtered

    This extender is called for every petition which is converted using to_api
    on the request.
    """

    NAME = 'Petition.extend'

    PUBLIC_OWNER_PROPS = [
        'id',
        'class',
        'firstname',
        'lastname',
    ]

    def __init__(self, request, docs):
        self.request = request
        self.docs = docs

    def extend(self, docs):
        if not docs:
            return
        if not self.request.has_permission(acl.Permissions.AdminFull):
            user = self.request.user
            if not user or (user.id != docs['owner']['id']):
                self.remove_private_data(docs)

    def remove_private_data(self, doc):
        owner = doc['owner']
        filtered_owner = {}
        for name in self.PUBLIC_OWNER_PROPS:
            if name in owner:
                filtered_owner[name] = owner[name]
        doc['owner'] = filtered_owner


APIExtender.register(PetitionExtender.NAME, PetitionExtender)
