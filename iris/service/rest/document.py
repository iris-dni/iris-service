class DocumentRESTMapperMixin(object):
    """A simple REST API mapper implementation for documents
    """

    DOC_CLASS = None

    def get(self, contentId):
        return self.doc_as_dict(self.DOC_CLASS.get(contentId))

    def create(self, data):
        doc = self.DOC_CLASS(**data)
        doc.store(refresh=True)
        return self.doc_as_dict(doc)

    def update(self, contentId, data):
        doc = self.DOC_CLASS.get(contentId)
        if not doc:
            return None
        for name, value in data.items():
            setattr(doc, name, value)
        doc.store(refresh=True)
        return self.doc_as_dict(doc)

    def delete(self, contentId):
        doc = self.DOC_CLASS.get(contentId)
        if doc is None:
            return
        doc.delete(refresh=True)
        return self.doc_as_dict(doc)

    def search(self, **kwargs):
        limit = int(kwargs.get('limit', 10))
        query = {
            "query": {
                "match_all": {}
            },
            "size": limit
        }
        result = self.DOC_CLASS.search(query)
        return {'data': map(lambda d: self.doc_as_dict(d),
                            result['hits']['hits']),
                'total': result['hits']['total']}

    def doc_as_dict(self, doc):
        """Provide the document as a dict to be able to JSON serialize it"""
        if doc is None:
            return None
        return doc.get_source()
