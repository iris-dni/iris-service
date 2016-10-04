from . import queries
from .extender import APIExtender
from .transform import APITransformer


class DocumentRESTMapperMixin(object):
    """A simple REST API mapper implementation for documents
    """

    DOC_CLASS = None

    def get(self, contentId, resolve=[], extend=[]):
        if isinstance(contentId, list):
            # remove empty ids
            if len(contentId) > 1:
                ids = [c for c in contentId if c]
                return self.to_api(self.DOC_CLASS.mget(ids),
                                   resolve,
                                   extend)
            contentId = contentId[0]
        return self.to_api(self.DOC_CLASS.get(contentId), resolve, extend)

    def create(self, data, resolve=[], extend=[]):
        doc = self.DOC_CLASS(**data['data'])
        doc.store(refresh=True)
        return self.to_api(doc, resolve, extend)

    def update(self, contentId, data, resolve=[], extend=[]):
        doc = self.DOC_CLASS.get(contentId)
        if not doc:
            return None
        for name, value in data['data'].items():
            setattr(doc, name, value)
        doc.store(refresh=True)
        return self.to_api(doc, resolve, extend)

    def delete(self, contentId):
        doc = self.DOC_CLASS.get(contentId)
        if doc is None:
            return
        doc.delete(refresh=True)
        return self.to_api(doc)

    def to_api(self, doc, resolve=[], extend=[]):
        """Provide the document as a dict to be able to JSON serialize it
        """
        if doc is None:
            return None
        extender = APIExtender(self.request, doc, extend)
        result = APITransformer(doc, resolve=resolve).to_api()
        extender.extend(result)
        return result


class SearchableDocumentRESTMapperMixin(object):

    """
    A list of allowed query parameters and their respective transformer.
    """
    QUERY_PARAMS = {}

    """
    Queries which are always available.
    """
    GENERIC_QUERY_PARAMS = {
        'terms_query': queries.genericTermsQuery
    }

    """
    A list of allowed filter parameters and their respective transformer.
    """
    FILTER_PARAMS = {}

    """
    Filters which are always available.
    """
    GENERIC_FILTER_PARAMS = {
        'terms_filter': queries.genericTermsQuery
    }

    """
    A list of allowed sort parameters and their respective transformer.
    The `default` key is used as default.
    """
    SORT_PARAMS = {
        'default': queries.scoreSorter
    }

    def search(self,
               offset=0,
               limit=10,
               sort=None,
               testing_only=False,
               debug=None,
               **params):
        filterMust = []
        queryMust = []
        order = []
        resolve = []
        extender = []

        if 'resolve' in params:
            resolve = params.pop('resolve') or []

        if 'extend' in params:
            extender = params.pop('extend') or []

        def add_sort(add):
            if not add:
                return
            if not isinstance(add, (list, tuple)):
                add = [add]
            order.extend(add)

        def sortOrder(s):
            return 'desc' if s[0:1] == '-' else 'asc'

        ids_only = 'ids_only' in params

        if sort is not None:
            try:
                for s in sort:
                    add_sort(self.SORT_PARAMS[s.strip('-')](sortOrder(s)))
            except KeyError as e:
                raise ValueError("Sorting '%s' not supported" % e.message)
        if not order and 'default' in self.SORT_PARAMS:
            # apply the sort default
            add_sort(self.SORT_PARAMS['default']('asc'))

        for key, value in params.items():
            if value is None:
                # Ignore None because missing query paramters are forwarded as
                # None by swagger.
                continue
            elif key in self.QUERY_PARAMS:
                queryMust.append(self.QUERY_PARAMS[key](value))
            elif key in self.GENERIC_QUERY_PARAMS:
                queryMust.append(self.GENERIC_QUERY_PARAMS[key](value))
            elif key in self.FILTER_PARAMS:
                filterMust.append(self.FILTER_PARAMS[key](value))
            elif key in self.GENERIC_FILTER_PARAMS:
                filterMust.append(self.GENERIC_FILTER_PARAMS[key](value))
            else:
                raise KeyError("Parameter '%s' not allowed" % key)
        self._extend_query(queryMust)
        self._extend_filter(filterMust)
        query = {
            "filtered": {
                "filter": {
                    "bool": {
                        "must": filterMust
                    }
                },
                "query": {
                    "bool": {
                        "must": queryMust
                    }
                }
            }
        }
        body = {
            "from": offset,
            "size": limit,
            "sort": order,
            "query": query,
        }
        if ids_only:
            body['fields'] = ["id"]
        result = {
            'data': [],
            'total': 0,
        }
        if not testing_only:
            searchresult = self.DOC_CLASS.search(body)
            hits = searchresult['hits']['hits']
            total = searchresult['hits']['total']
            data = []
            if ids_only:
                data = [d['fields']['id'][0] for d in hits]
            else:
                data = self.to_api(hits, resolve, extender)
            result = {
                'data': data,
                'total': total,
            }
        if debug or testing_only:
            result['debug'] = {
                'index': self.DOC_CLASS.INDEX,
                'doc_type': self.DOC_CLASS.DOC_TYPE,
                'query': body
            }
        return result

    def _extend_query(self, query):
        pass

    def _extend_filter(self, filters):
        pass
