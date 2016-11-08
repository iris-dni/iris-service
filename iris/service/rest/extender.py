import itertools


class APIExtender(object):
    """Extend API response data for documents

    Allows to use registered extenders using the `extend` query request
    parameter.

    Additional the extender checks if there is an extender with the name
    `<__class__.__name__>` and executes it. This can be used to do additional
    operations on the response data without the need of an explicit request of
    the extend.
    """

    EXTENDER_REGISTRY = {}

    def __init__(self, request, docs, extenders=None):
        self.request = request
        if not isinstance(docs, list):
            self.docs = [docs]
        else:
            self.docs = docs
        self.extenders = []
        self._build_extenders(extenders)

    def extend(self, docs):
        for extender in self.extenders:
            extender.extend(docs)
        for doc, api_doc in itertools.izip(self.docs, docs):
            if doc is None or api_doc is None:
                continue
            secure_name = doc.__class__.__name__ + '.secure'
            if secure_name not in self.EXTENDER_REGISTRY:
                continue
            self.EXTENDER_REGISTRY[secure_name](self.request,
                                                doc
                                               ).extend(api_doc)

    def _build_extenders(self, extenders):
        if not extenders:
            return
        for extender in extenders:
            if extender in self.EXTENDER_REGISTRY:
                self.extenders.append(
                    self.EXTENDER_REGISTRY[extender](self.request, self.docs)
                )

    @classmethod
    def applyExtensionData(cls, doc, name, data):
        """Can be used by extenders to apply extension data

        doc: must be the result document which is then used in the API
        name: is the name of the extension
        data: is the data which should be applied as extension data
        """
        extension = doc.setdefault('extensions', {})
        extension[name] = data

    @classmethod
    def register(cls, name, extender):
        cls.EXTENDER_REGISTRY[name] = extender
