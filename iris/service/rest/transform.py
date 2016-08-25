import inspect

from lovely.esdb.properties import Relation, RelationResolver


class APITransformer(object):
    """
    """

    def __init__(self, doc, resolve=None):
        self.single_doc = not isinstance(doc, list)
        if self.single_doc:
            self.docs = [doc]
        else:
            self.docs = doc
        self.resolve = resolve or []
        self.resolved = {}
        self.build_name_layer()

    def to_api(self):
        """Provide the document as a dict for the API
        """
        sources = self.build_resolveable_source()
        relations = self.extract_relations_to_resolve(sources)
        self.resolve_relations(relations)
        self.prepare_result(sources)
        if self.single_doc:
            sources = sources[0]
        return sources

    def build_resolveable_source(self):
        """Build the source for all docs of the transformer
        """
        return [self.build_doc_source(doc) for doc in self.docs]

    def build_doc_source(self, doc):
        """Build the source for a document
        """
        if doc is None:
            return None
        source = doc.get_source()
        for name, relation in self._iter_relations(doc):
            source[name] = getattr(doc, name)
        if '_relations' in source:
            del source['_relations']
        return source

    def prepare_result(self, sources):
        """Replaces relations

        If a relation is in the resolve list it will be expanded with the
        resolved document.
        """
        for doc in sources:
            for name, relation in self._iter_source_relations(doc):
                rel_data = relation.relation_dict
                if name in self.resolve:
                    rel_data['data'] = self.resolved.get(relation.remote,
                                                         {}
                                                        ).get(relation.id)
                doc[name] = rel_data

    def extract_relations_to_resolve(self, sources):
        """Build a mapping with relations to resolve

        The resilt is a mapping where the key is the document class and the
        values are sets with the ids of the documents to resolve.
        """
        relations = {}
        for source in sources:
            for name, value in self._iter_source_relations(source):
                if name in self.resolve and value.id is not None:
                    remote = relations.setdefault(value.remote, set([]))
                    remote.add(value.id)
        return relations

    def resolve_relations(self, relations):
        for doc_class, ids in relations.iteritems():
            ids = list(ids)
            docs = doc_class.mget(ids)
            class_docs = self.resolved.setdefault(doc_class, {})
            for i, doc in enumerate(docs):
                class_docs[ids[i]] = self.build_doc_source(doc)

    def build_name_layer(self):
        self.name_layer = {}

        def assign_name(name, layer):
            parts = name.split('.', 1)
            names = layer.setdefault(parts[0], {})
            if len(parts) < 2:
                return
            assign_name(parts[1], names)
        for name in self.resolve:
            assign_name(name, self.name_layer)

    @staticmethod
    def _iter_relations(doc):
        """yield the relation properties of a document
        """
        def isRelation(obj):
            return isinstance(obj, Relation)
        for (name, prop) in inspect.getmembers(doc.__class__, isRelation):
            yield (name, prop)

    @staticmethod
    def _iter_source_relations(doc):
        """yield the relation resolver properties of a document source
        """
        for name, prop in doc.iteritems():
            if isinstance(prop, RelationResolver):
                yield (name, prop)
