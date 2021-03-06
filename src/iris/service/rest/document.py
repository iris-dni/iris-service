from . import queries


class DocumentRESTMapperMixin(object):
    """A simple REST API mapper implementation for documents
    """

    DOC_CLASS = None

    def get(self, contentId, resolve=None, extend=None):
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
        doc_data = data['data']
        self._prepare_data(None, doc_data)
        doc = self.DOC_CLASS(**doc_data)
        self._prepare_document(doc, doc_data, True)
        doc.store(refresh=True)
        return self.to_api(doc, resolve, extend)

    def update(self, contentId, data, resolve=[], extend=[]):
        doc = self.DOC_CLASS.get(contentId)
        if not doc:
            return None
        doc_data = data['data']
        self._prepare_data(doc, doc_data)
        for name, value in doc_data.items():
            setattr(doc, name, value)
        self._prepare_document(doc, doc_data, False)
        doc.store(refresh=True)
        return self.to_api(doc, resolve, extend)

    def delete(self, contentId):
        doc = self.DOC_CLASS.get(contentId)
        if doc is None:
            return
        doc.delete(refresh=True)
        return self.to_api(doc)

    def to_api(self, doc, resolve=None, extend=None):
        """Provide the document as a dict to be able to JSON serialize it
        """
        return self.request.to_api(doc, resolve, extend)

    def _prepare_data(self, doc, data):
        """Prepare the received data before assignement to doc

        This is called from create and update to give subclasses the chance to
        manipulate the received data before it is assigned to the document.
        doc is None if this is a create request otherwise it is the document
        before it is manipulated.
        """
        pass

    def _prepare_document(self, doc, data, is_create):
        """Prepare the received data before the document is stored

        This is called from create and update to give subclasses the chance to
        manipulate the document just before it is stored.
        """
        pass


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
        ids_only = 'ids_only' in params

        def add_sort(add):
            if not add:
                return
            if not isinstance(add, (list, tuple)):
                add = [add]
            order.extend(add)

        def sortOrder(s):
            return 'desc' if s[0:1] == '-' else 'asc'

        if sort is not None:
            try:
                for s in sort:
                    sorter = self.SORT_PARAMS[s.strip('-')](sortOrder(s))
                    if sortOrder is not None:
                        add_sort(sorter)
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
            elif key not in ['resolve', 'extend', 'ids_only']:
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
        return self._do_query(body, ids_only, testing_only, debug)

    def _do_query(self, body, ids_only, testing_only, debug):
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
                data = self.to_api(hits)
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
