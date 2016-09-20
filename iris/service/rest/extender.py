

class APIExtender(object):
    """
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

        doc must be the result document which is the used in the API
        name is the name of the extension
        data is the data which should be applied as extension data
        """
        extension = doc.setdefault('extensions', {})
        extension[name] = data

    @classmethod
    def register(cls, name, extender):
        cls.EXTENDER_REGISTRY[name] = extender
