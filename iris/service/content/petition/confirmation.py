# -*- coding: utf-8 -*-
import time
import datetime
import random

from iris.service import rest

from iris.service.db.dc import dc_update, iso_now_offset
from iris.service.content.confirmation.handler import Handler
from iris.service.content.confirmation import Confirmation
from iris.service import sms

from .document import Petition, Supporter
from .mail import send_petition_mail


SMS_TEXT = u'Dein code für petitio.ch ist\n %s'


class SMSBaseHandler(Handler):

    ALLOW_API_CONFIRM = False

    def build_token(self, confirmation, petition=None):
        if petition is None:
            petition = self._petition(confirmation)
        while True:
            token = str(random.randint(10000, 99999))
            confirmation.data['token'] = token
            context_id = self.build_context_id(petition, token)
            if not Confirmation.has_active_context_id(context_id):
                break
        confirmation.context_id = context_id

    def _petition(self, confirmation):
        return Petition.get(confirmation.data['petition'])

    @classmethod
    def handle_confirmation(cls, request, petition, token):
        confirmation = Confirmation.get_active_context_id(
            cls.build_context_id(petition, token)
        )
        if confirmation is not None:
            return Handler.confirm_handler(
                confirmation.handler,
                confirmation.id,
                request,
                petition=petition
            )
        raise ValueError('context_id not found or expired')

    @classmethod
    def build_context_id(cls, petition, token):
        return petition.id + '-' + token


class PetitionSMSHandler(SMSBaseHandler, rest.RESTMapper):
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
        self.build_token(confirmation, petition)
        text = SMS_TEXT % confirmation.data['token']
        confirmation.debug['sms'] = {
            'phone_number': mobile,
            'text': text,
            'response': sms.sendSMS(mobile, text)
        }
        confirmation.response['petition'] = petition.id

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


class SupportSMSHandler(SMSBaseHandler, rest.RESTMapper):
    """SMS confirmation handler for supports

    """

    HANDLER_NAME = 'support_sms'
    NAME = 'confirmations.' + HANDLER_NAME

    def _create(self, confirmation):
        """Send an SMS with the confirmation id
        """
        dc_update(
            confirmation,
            expires=iso_now_offset(datetime.timedelta(minutes=5)),
        )
        mobile = confirmation.data['user']['mobile']
        self.build_token(confirmation)
        text = SMS_TEXT % confirmation.data['token']
        confirmation.debug['sms'] = {
            'phone_number': mobile,
            'text': text,
            'response': sms.sendSMS(mobile, text)
        }
        confirmation.response['petition'] = self._petition(confirmation).id

    def _confirm(self, confirmation, **kwargs):
        """Nothing to do here

        The confirmation is handled in the "support" endpoint which provides
        the confirmation token and just calls confirm.
        """
        pass


class PetitionEMailConfirmHandler(Handler, rest.RESTMapper):
    """Email confirmation handler for petitions
    """

    HANDLER_NAME = 'petition_confirm_email'
    NAME = 'confirmations.' + HANDLER_NAME

    TEMPLATE = 'iris-petition-mailconfirmation'

    def needs_confirmation(self, data):
        """Do not create a new confirmation mail if there is a pending mail
        """
        data = data['data']
        context_id = self.TEMPLATE + data['petition']
        c = Confirmation.search({
            "query": {
                "bool": {
                    "must": [
                        {"term": {"handler": self.HANDLER_NAME}},
                        {"term": {"context_id": context_id}},
                        {
                            "range": {
                                "context_id": {"gt": int(time.time() * 1000)}
                            }
                        },
                    ]
                }
            },
            'size': 0
        })
        return c['hits']['total'] == 0

    def _create(self, confirmation):
        """Send a Mail with the confirmation url
        """
        petition = self._petition(confirmation)
        email = petition.owner.relation_dict.get('email')
        if not email:
            raise ValueError('Missing email')
        confirmation.data['email'] = email
        dc_update(
            confirmation,
            expires=iso_now_offset(datetime.timedelta(days=30)),
        )
        mail_data = {
            'confirm': {
                'url': self._confirm_url(confirmation.id)
            }
        }
        confirmation.debug['mail'] = send_petition_mail(
            self.request,
            self.TEMPLATE,
            petition,
            [petition.owner.relation_dict],
            mail_data
        )
        confirmation.response['petition'] = petition.id
        confirmation.context_id = self.TEMPLATE + petition.id

    def _confirm(self, confirmation, petition=None):
        """Confirms the mobile number on the petition

        If the mobile number on the owner relation matches the mobile number
        of this confirmation the email_trusted flag is set to true.
        """
        if petition is None:
            petition = self._petition(confirmation)
        email = petition.owner.relation_dict['email']
        if email != confirmation.data['email']:
            raise ValueError('EMail not matching')
        petition.owner = {"email_trusted": True}
        petition.store(refresh=True)

    def _petition(self, confirmation):
        return Petition.get(confirmation.data['petition'])

    def _confirm_url(self, key):
        from iris.service.content.petition import SETTINGS
        fe = SETTINGS['frontend']
        return fe['domain'] + fe['petition-email-confirmpath'] + '?key=' + key


class SupportEMailConfirmHandler(Handler, rest.RESTMapper):
    """Email confirmation handler for supporters
    """

    HANDLER_NAME = 'supporter_confirm_email'
    NAME = 'confirmations.' + HANDLER_NAME

    TEMPLATE = 'iris-supporter-mailconfirmation'

    def _create(self, confirmation):
        """Send a Mail with the confirmation url
        """
        supporter = self._supporter(confirmation)
        email = supporter.user.relation_dict.get('email')
        if not email:
            raise ValueError('Missing email')
        confirmation.data['email'] = email
        dc_update(
            confirmation,
            expires=iso_now_offset(datetime.timedelta(days=30)),
        )
        mail_data = {
            'confirm': {
                'url': self._confirm_url(confirmation.id)
            }
        }
        petition = self._petition(confirmation)
        confirmation.debug['mail'] = send_petition_mail(
            self.request,
            self.TEMPLATE,
            petition,
            [supporter.user.relation_dict],
            mail_data
        )
        confirmation.response['petition'] = petition.id

    def _confirm(self, confirmation, petition=None):
        """Confirms the mobile number on the petition

        If the mobile number on the owner relation matches the mobile number
        of this conrimation the mobile_trusted flag is set to true.
        """
        supporter = self._supporter(confirmation)
        email = supporter.user.relation_dict['email']
        if email != confirmation.data['email']:
            raise ValueError('EMail not matching')
        supporter.user = {"email_trusted": True}
        supporter.store(refresh=True)

    def _petition(self, confirmation):
        return Petition.get(confirmation.data['petition'])

    def _supporter(self, confirmation):
        return Supporter.get(confirmation.data['supporter'])

    def _confirm_url(self, key):
        from iris.service.content.petition import SETTINGS
        fe = SETTINGS['frontend']
        return fe['domain'] + fe['supporter-email-confirmpath'] + '?key=' + key
