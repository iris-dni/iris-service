from iris.service import rest

from .document import Confirmation


class Handler(rest.DocumentRESTMapperMixin):

    def create(self, data, resolve=[], extend=[]):
        confirmation = Confirmation(handler=self.HANDLER_NAME,
                                    **data['data'])
        self._create(confirmation)
        confirmation.store(refresh=True)
        return self.to_api(confirmation, resolve, extend)

    def confirm(self, confirmation, resolve=[], extend=[]):
        if confirmation.state == 'used':
            raise ValueError("Already used")
        if confirmation.expired:
            raise ValueError("Expired")
        self._confirm(confirmation)
        confirmation.state = 'used'
        confirmation.store(refresh=True)
        return self.to_api(confirmation, resolve, extend)

    def _create(self, confirmation):
        pass

    def _confirm(self, confirmation):
        pass

    @classmethod
    def create_for_handler(cls, handler_name, data, request=None):
        handler = rest.RESTMapper.getMapperImplementation(
            'confirmations.' + handler_name,
            request,
        )
        return handler.create({"data": data})
