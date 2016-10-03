import datetime

from iris.service import rest

from iris.service.db.dc import dc_update, dc_now_offset
from iris.service.content.confirmation.handler import Handler
from .document import Petition


class SMSHandler(Handler, rest.RESTMapper):
    """SMS confirmation handler for petitions

    """

    HANDLER_NAME = 'petition_sms'
    NAME = 'confirmations.' + HANDLER_NAME

    def _create(self, confirmation):
        """Send an SMS with the confirmation id
        """
        petition = self._petition(confirmation)
        mobile = petition.owner.relation_dict.get('mobile')
        if not mobile:
            raise ValueError('Missing mobile number')
        confirmation.data['mobile'] = mobile
        dc_update(
            confirmation,
            expires=dc_now_offset(datetime.timedelta(minutes=5)),
        )

    def _confirm(self, confirmation):
        petition = self._petition(confirmation)
        mobile = petition.owner.relation_dict['mobile']
        if mobile != confirmation.data['mobile']:
            raise ValueError('Mobile number not matching')
        petition.owner = {"mobile_trusted": True}
        petition.store(refresh=True)

    def _petition(self, confirmation):
        return Petition.get(confirmation.data['petition'])
