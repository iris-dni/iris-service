import inspect

from lovely.esdb.properties import (
    LocalRelation,
    RelationResolver,
)
from lovely.esdb.properties.relation import (
    ListRelationResolver,
)


class APITransformer(object):
    """
    """

    def __init__(self, doc, resolve=None):
        """Setup the transformer

        resolve is a list of dotted property names to be resolved.
        """
        self.single_doc = not isinstance(doc, list)
        if self.single_doc:
            self.docs = [doc]
        else:
            self.docs = doc
        self.resolve = self.build_resolve_names(resolve)
        self.resolved = {}
        self.depth = 0

    def build_resolve_names(self, names):
        result = []
        for name in (names or []):
            parts = name.split('.')
            for n in range(len(parts)):
                result.append('.'.join(parts[:n + 1]))
        return result

    def to_api(self):
        """Provide the document as a dict for the API
        """
        self.depth = 0
        source_docs = self.build_resolveable_source()
        sources = {'': source_docs}
        self.to_resolve = []
        while sources:
            relations = self.extract_relations_to_resolve(sources)
            self.resolve_relations(relations)
            sources = self.prepare_result(sources, resolved=True)
        if self.single_doc:
            return source_docs[0]
        return source_docs

    def build_resolveable_source(self):
        """Build the source for all docs of the transformer
        """
        return [self.build_doc_source(doc) for doc in self.docs]

    def extract_relations_to_resolve(self, sources):
        """Build a mapping with relations to resolve

        sources must be a dict::
            {
                '': [docs],
                ...
            }
        The key is the base name in the parent source and allows deep
        resolving.

        The result is a mapping where the key is the document class and the
        values are sets with the ids of the documents to resolve.

        Example result:
            {
                DocClass: ['324', '333']
            }
        """
        relations = {}
        for basename, docs in sources.items():
            for source in docs:
                for name, value in self._iter_source_relations(source):
                    full_name = self.build_rel_name(basename, name)
                    if full_name not in self.resolve:
                        continue
                    if not isinstance(value, ListRelationResolver):
                        value = [value]
                    for v in value:
                        if v.id is not None:
                            remote = relations.setdefault(v.remote, set([]))
                            remote.add(v.id)
        return relations

    def build_rel_name(self, base, name):
        if not base:
            return name
        return '.'.join((base, name))

    def resolve_relations(self, relations):
        """From a class to ids mapping get the objects

        relations is the output from extract_relations_to_resolve in the form:
            {
                DocClass: [ids],
                ...
            }

        Stores the resolved objects in self.resolved.

        Example structure of self.resolved:
            {
                DocClass: {
                    <doc_id>: <doc source>,
                    <doc_id>: <doc source>
                },
                ...
            }
        """
        for doc_class, ids in relations.iteritems():
            ids = list(ids)
            docs = doc_class.mget(ids)
            class_docs = self.resolved.setdefault(doc_class, {})
            for i, doc in enumerate(docs):
                class_docs[ids[i]] = self.build_doc_source(doc)

    def build_doc_source(self, doc):
        """Build the source for a document

        Uses get_source on doc to get the JSON source.
        Adds the relation properties to the result.
        Removes _relations if doc provides it.
        """
        if doc is None:
            return None
        source = doc.get_source()
        for name, relation in self._iter_relations(doc):
            source[name] = getattr(doc, name)
        if '_relations' in source:
            del source['_relations']
        return source

    def prepare_result(self, sources, resolved):
        """Replaces relations from a list of source documents.

        Relation properties are replaced with the relation_dict of the
        relation.

        If a relation is in the resolve list it will be expanded with the
        resolved document.

        This will also update self.to_resolve with the documents in the next
        resolve depth.

        Returns the next level of resolve. The response can be used as the
        input for extract_relations_to_resolve and is in the form::
            {
                '<relName>': [docs],
                ...
            }
        """
        docs = {}
        self._prepare_result(sources, resolved, docs)
        return docs

    def _prepare_result(self, sources, resolved, docs):
        for basename, doc_sources in sources.items():
            for doc in doc_sources:
                for name, relation in self._iter_source_relations(doc):
                    rel_data = relation.relation_dict
                    doc[name] = rel_data
                    if not resolved:
                        continue
                    full_name = self.build_rel_name(basename, name)
                    if full_name not in self.resolve:
                        continue
                    doc_list = docs.setdefault(full_name, [])
                    if isinstance(relation, ListRelationResolver):
                        for item in rel_data:
                            d = self.resolved.get(relation.remote,
                                                  {}
                                                 ).get(item["id"])
                            if d is not None:
                                doc_list.append(d)
                            item['data'] = d
                    else:
                        d = self.resolved.get(relation.remote,
                                              {}
                                             ).get(relation.id)
                        if d is not None:
                            doc_list.append(d)
                        rel_data['data'] = d

    @staticmethod
    def _iter_relations(doc):
        """yield the relation properties of a document
        """
        if doc is None:
            return

        def isRelation(obj):
            return isinstance(obj, LocalRelation)
        for (name, prop) in inspect.getmembers(doc.__class__, isRelation):
            yield (name, prop)

    @staticmethod
    def _iter_source_relations(doc):
        """yield the relation resolver properties of a document source
        """
        if doc is None:
            return
        for name, prop in doc.iteritems():
            if isinstance(prop, (RelationResolver, ListRelationResolver)):
                yield (name, prop)
