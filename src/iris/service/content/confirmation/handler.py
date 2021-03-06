from iris.service import rest

from .document import Confirmation


class Handler(rest.DocumentRESTMapperMixin):

    ALLOW_API_CONFIRM = True

    def create(self, data):
        confirmation = Confirmation(handler=self.HANDLER_NAME,
                                    **data['data'])
        self._create(confirmation)
        confirmation.store(refresh=True)
        return self.to_api(confirmation)

    def confirm(self, confirmation, **kwargs):
        if confirmation.state == 'used':
            raise ValueError("Already used")
        if confirmation.expired:
            raise ValueError("Expired")
        self._confirm(confirmation, **kwargs)
        confirmation.state = 'used'
        confirmation.store(refresh=True)
        return confirmation.response

    def needs_confirmation(self, data):
        """Check if a confirmation is needed for the data

        This is used in the create_for_handler method to give handlers the
        chance to not create a confirmation.
        """
        return True

    def _create(self, confirmation):
        pass

    def _confirm(self, confirmation, **kwargs):
        pass

    @classmethod
    def create_for_handler(cls, handler_name, data, request=None):
        handler = rest.RESTMapper.getMapperImplementation(
            'confirmations.' + handler_name,
            request,
        )
        if handler.needs_confirmation(data):
            return handler.create({"data": data})
        return None

    @classmethod
    def confirm_handler(cls, handler_name, token, request=None, **kwargs):
        handler = rest.RESTMapper.getMapperImplementation(
            'confirmations.' + handler_name,
            request,
        )
        confirmation = Confirmation.get(token)
        if confirmation is None:
            raise ValueError('Confirmation "%s" not found' % token)
        return handler.confirm(confirmation, **kwargs)
