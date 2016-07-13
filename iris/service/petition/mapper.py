from iris.service.service import rest

from .document import Petition


class DocumentRESTMapperMixin(object):

    DOC_CLASS = None

    def get(self, contentId):
        return self.DOC_CLASS.get(contentId).get_source()

    def create(self, data):
        doc = self.DOC_CLASS(**data)
        doc.store(refresh=True)
        return doc.get_source()

    def update(self, contentId, data):
        doc = self.DOC_CLASS.get(contentId)
        if not doc:
            return None
        for name, value in data.items():
            setattr(doc, name, value)
        doc.store(refresh=True)
        return doc.get_source()

    def query(self, **kwargs):
        limit = int(kwargs.get('limit', 10))
        query = {
            "query": {
                "match_all": {}
            },
            "size": limit
        }
        try:
            result = self.DOC_CLASS.search(query)
        except Exception as e:
            raise
        return {'data': map(lambda d: d.get_source(), result['hits']['hits']),
                'total': result['hits']['total']}


class PetitionsRESTMapper(DocumentRESTMapperMixin, rest.RESTMapper):

    NAME = 'petitions'

    DOC_CLASS = Petition
