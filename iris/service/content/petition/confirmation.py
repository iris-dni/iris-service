import datetime

from iris.service import rest

from iris.service.db.dc import dc_update, iso_now_offset
from iris.service.content.confirmation.handler import Handler
from iris.service import sms

from .document import Petition


class PetitionSMSHandler(Handler, rest.RESTMapper):
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
            expires=iso_now_offset(datetime.timedelta(minutes=5)),
        )
        subject = 'Petition'
        text = 'Your verification code is "%s"' % confirmation.id
        confirmation.debug['sms'] = {
            'phone_number': mobile,
            'subject': subject,
            'text': text,
            'response': sms.sendSMS(mobile, subject, text)
        }

    def _confirm(self, confirmation, petition=None):
        """Confirms the mobile number on the petition

        If the mobile number on the owner relation matches the mobile number
        of this conrimation the mobile_trusted flag is set to true.
        """
        if petition is None:
            petition = self._petition(confirmation)
        mobile = petition.owner.relation_dict['mobile']
        if mobile != confirmation.data['mobile']:
            raise ValueError('Mobile number not matching')
        petition.owner = {"mobile_trusted": True}
        petition.store(refresh=True)

    def _petition(self, confirmation):
        return Petition.get(confirmation.data['petition'])


class SupportSMSHandler(Handler, rest.RESTMapper):
    """SMS confirmation handler for supports

    """

    HANDLER_NAME = 'support_sms'
    NAME = 'confirmations.' + HANDLER_NAME

    ALLOW_API_CONFIRM = False

    def _create(self, confirmation):
        """Send an SMS with the confirmation id
        """
        dc_update(
            confirmation,
            expires=iso_now_offset(datetime.timedelta(minutes=5)),
        )
        mobile = confirmation.data['user']['mobile']
        subject = 'Support'
        text = 'Your verification code is "%s"' % confirmation.id
        confirmation.debug['sms'] = {
            'phone_number': mobile,
            'subject': subject,
            'text': text,
            'response': sms.sendSMS(mobile, subject, text)
        }

    def _confirm(self, confirmation):
        """Nothing to do here

        The confirmation is handled in the "support" endpoint which provides
        the confirmation token and just calls confirm.
        """
        pass
