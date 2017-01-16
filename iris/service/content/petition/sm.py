import copy
import yaml
import os
from datetime import timedelta
import dateutil.parser

import transitions
from transitions.extensions import MachineFactory
from transitions.extensions.nesting import NestedState

from iris.service.db import dc
from iris.service.db.sequence import IID_SHORTED

from iris.service.rest import swagger

from iris.service.content.confirmation.handler import Handler
from iris.service.content.city.document import TRESHOLD_NOT_SET
from iris.service.content.user import SessionUser, normalise_phone_number

from .mail import send_petition_mail


# create a state machine implementation from extensions
Machine = MachineFactory.get_predefined(nested=True)
NestedState.separator = '.'


APPROVAL_DAYS = 30
BEFORE_LOSER_DAYS = 2
LETTER_WAIT_DAYS = 40

SMS_VERIFICATION = True


class ConditionError(Exception):

    def __init__(self, reasons, data=None):
        self.reasons = reasons
        self.data = data
        super(ConditionError, self).__init__("400")


def condition_error_request_handler(exc, request):
    """Handles response for ConditionError

    Renders a proper json response
    """
    request.response.status = 200
    return swagger.reduce_result(
        request,
        {
            "data": exc.data,
            "reasons": exc.reasons,
            "status": "error"
        }
    )


class PetitionStateMachine(object):

    def __init__(self, petition, request):
        self.petition = petition
        self.request = request
        self.sm = Machine(
            self,
            initial=petition.state.full_name,
            **fromYAML()
        )

    def set_state(self, value):
        """Set the state on the petition
        """
        self.petition.state.full_name = value

    def get_state(self):
        """Get the state from the petition
        """
        return self.petition.state.full_name

    state = property(get_state, set_state)

    def force_state(self, to_state, **kwargs):
        """Allow to force a state independent of the statemachine

        This is a developer tool to be able to force the statemachine into any
        state.
        """
        transition = transitions.Transition(self.state, to_state)
        event_data = transitions.EventData(
            state=None,
            event=None,
            machine=self.sm,
            model=self,
            args=[],
            kwargs={}
        )
        # sets the state to the current state instance
        event_data.update()
        return transition.execute(event_data)

    def listable(self, **kwargs):
        self.petition.state.listable = True

    def not_listable(self, **kwargs):
        self.petition.state.listable = False

    def enable_tick(self, **kwargs):
        self.petition.state.tick = True

    def disable_tick(self, **kwargs):
        self.petition.state.tick = False

    def check_publish(self, **kwargs):
        """Check if publishing is possible

        This is called on the publish event in state draft.
        Here we need to check if the publishing is allowed and provide an
        exception for the view code to render an appropriate response.
        """
        global SMS_VERIFICATION
        missing = []
        owner_rel = self.petition.owner.relation_dict
        for required in ['mobile', 'email']:
            if not owner_rel.get(required):
                missing.append(required + '_missing')
        if missing:
            data = self.request.to_api(self.petition)
            raise ConditionError(missing, data)
        untrusted = []
        if SMS_VERIFICATION and not owner_rel.get('mobile_trusted'):
            token = kwargs['data'].get('mobile_token')
            if token:
                from .confirmation import SMSBaseHandler
                try:
                    SMSBaseHandler.handle_confirmation(
                        self.request,
                        self.petition,
                        token,
                    )
                except ValueError:
                    untrusted.append("mobile_verification_failed")
            else:
                untrusted.append('mobile_untrusted')
                data = {
                    "data": {
                        "petition": self.petition.id
                    }
                }
                Handler.create_for_handler('petition_sms',
                                           data,
                                           self.request)
        if untrusted:
            data = self.request.to_api(self.petition)
            raise ConditionError(untrusted, data)
        if not owner_rel.get('email_trusted'):
            # send a confirmation email
            data = {
                "data": {
                    "petition": self.petition.id,
                }
            }
            Handler.create_for_handler('petition_confirm_email',
                                       data,
                                       self.request)

    def support_petition_on_publish(self, **kwargs):
        """Petition owner supports when publishing

        The data used for the supporter is based on the owner data stored on
        the petition.
        """
        data = copy.deepcopy(self.petition.owner.relation_dict)
        user = data['id']
        del data['id']
        del data['class']
        self.petition.addSupporter(request=self.request,
                                   user_id=user,
                                   data=data)

    def support_petition(self, **kwargs):
        """Check if supporting is allowed

        This is called on the transition of trigger "support".
        """
        global SMS_VERIFICATION
        data = kwargs['data']
        user_data = data['user']
        session_user = self.request.session_user
        if session_user is not None:
            session_user = session_user.id
        if self.petition.isSupporting(request=self.request,
                                      user_id=session_user,
                                      data=user_data):
            raise ConditionError(["User already supports this petition"])
        user = self.request.user
        if SessionUser.is_session_user(user):
            user = None
        untrusted = []
        mobile = normalise_phone_number(user_data['mobile'])
        mobile_trusted = (user and
                          user.mobile == mobile and
                          user.mobile_trusted)
        if SMS_VERIFICATION and not mobile_trusted:
            # Here we have an untrusted mobile number because the logged in
            # user has a different mobile than the provided one or the users
            # mobile is also not trusted.
            token = data.get('mobile_token')
            if token:
                # check if the token matches the mobile number
                msg = None
                from .confirmation import SMSBaseHandler
                try:
                    msg = SMSBaseHandler.handle_confirmation(
                        self.request,
                        self.petition,
                        token,
                    )
                except ValueError:
                    # a ValueError means that confirmation failed
                    pass
                if msg:
                    # We trust the mobile because the verification token is
                    # correct.
                    mobile_trusted = True
                else:
                    untrusted.append('mobile_verification_failed')
            else:
                # We have an untrusted mobile number, send an SMS with the
                # verification code.
                untrusted.append('mobile_untrusted')
                data = {
                    "data": {
                        "user_id": user and user.id,
                        "user": user_data,
                        "petition": self.petition.id
                    }
                }
                Handler.create_for_handler('support_sms',
                                           data,
                                           self.request)
        if untrusted:
            data = self.request.to_api(self.petition)
            raise ConditionError(untrusted, data)
        user_data['mobile_trusted'] = mobile_trusted
        email = user_data.get('email')
        email_trusted = (user and
                         email and
                         user.email == email and
                         user.email_trusted)
        user_data['email_trusted'] = email_trusted
        # support the petition
        supporter = self.petition.addSupporter(
            request=self.request,
            user_id=session_user,
            data=user_data)
        from .confirmation import SMSBaseHandler
        SMSBaseHandler.trust_user_mobile(supporter.user)
        if email and not email_trusted:
            # send a confirmation email
            data = {
                "data": {
                    "petition": self.petition.id,
                    "supporter": supporter.id,
                }
            }
            Handler.create_for_handler('supporter_confirm_email',
                                       data,
                                       self.request)

    def set_response_token(self, **kwargs):
        """Sets a new response token if no token is set
        """
        token = self.petition.response_token
        if token is None:
            self.petition.response_token = IID_SHORTED()

    def reset_response_token(self, **kwargs):
        """Reset the response token
        """
        self.petition.response_token = None

    def if_feedback_has_valid_token(self, data, **kwargs):
        return self.petition.response_token == data['token']

    def set_petition_feedback(self, data, **kwargs):
        self.petition.city_answer = data['answer']

    def start_support(self, **kwargs):
        """Called when switching into a support state

        Sets dc.effective to the current time and dc.expires to current time +
        APPROVAL_DAYS.
        """
        global APPROVAL_DAYS
        dc.dc_update(self.petition,
                     **{dc.DC_EFFECTIVE: dc.time_now(),
                        dc.DC_EXPIRES: dc.time_now_offset(
                            timedelta(days=APPROVAL_DAYS)
                        ),
                       }
                    )
        self.petition.state.half_time_mail_time = dc.iso_now_offset(
            timedelta(days=APPROVAL_DAYS / 2)
        )()
        self.petition.state.before_loser_mail_time = dc.iso_now_offset(
            timedelta(days=APPROVAL_DAYS - BEFORE_LOSER_DAYS)
        )()

    def reset_support_start_timer(self, **kwargs):
        self.start_support()

    def set_letter_expire(self, **kwargs):
        global LETTER_WAIT_DAYS
        self.petition.state.letter_wait_expire = dc.iso_now_offset(
            timedelta(days=LETTER_WAIT_DAYS)
        )()

    def if_support_timeout(self, **kwargs):
        """Check if support time is over

        If the current time is past dc.expires support time is over.
        """
        times = dc.dc_time(self.petition)
        expire = times.get(dc.DC_EXPIRES, None)
        return not expire or expire <= dc.time_now()

    def if_no_letter_timeout(self, **kwargs):
        expire = dateutil.parser.parse(self.petition.state.letter_wait_expire)
        return not expire or expire <= dc.time_now()

    def if_supporter_limit_reached(self, **kwargs):
        """Check if the supporter treshold is reached
        """
        supporters = self.petition.supporters
        required = supporters.get('required')
        if required == TRESHOLD_NOT_SET:
            return False
        return supporters['amount'] >= required

    def if_city_assigned(self, **kwargs):
        return self.petition.city() is not None

    def if_send_half_time_mail(self, **kwargs):
        t = self.petition.state.half_time_mail_time
        if t is None:
            return False
        half_time = dateutil.parser.parse(t)
        result = half_time and half_time <= dc.time_now()
        if result:
            # Set to None to prevent from sending multiple time
            self.petition.state.half_time_mail_time = None
        return result

    def if_send_before_loser_mail(self, **kwargs):
        t = self.petition.state.before_loser_mail_time
        if t is None:
            return False
        before_time = dateutil.parser.parse(t)
        result = before_time and before_time <= dc.time_now()
        if result:
            # Set to None to prevent from sending multiple time
            self.petition.state.before_loser_mail_time = None
        return result

    def send_rejected_mail_to_owner(self, **kwargs):
        self._send_mail_to_petition_owner('iris-petition-rejected')

    def send_approval_mail_to_owner(self, **kwargs):
        self._send_mail_to_petition_owner('iris-petition-approved')

    def send_half_time_mail_to_owner(self, **kwargs):
        self._send_mail_to_petition_owner(
            'iris-petition-supportable-half-time')

    def send_before_loser_mail_to_owner(self, **kwargs):
        self._send_mail_to_petition_owner(
            'iris-petition-supportable-final-spurt')

    def send_winner_mail_to_owner(self, **kwargs):
        self._send_mail_to_petition_owner('iris-petition-winner')

    def send_lettersent_mail_to_owner(self, **kwargs):
        self._send_mail_to_petition_owner('iris-petition-letter-sent')

    def send_closed_without_response_mail_to_owner(self, **kwargs):
        self._send_mail_to_petition_owner(
            'iris-petition-closed-without-response')

    def send_loser_mail_to_owner(self, **kwargs):
        self._send_mail_to_petition_owner(
            'iris-petition-loser-notification-for-owner')

    def send_loser_mail_to_supporters(self, **kwargs):
        self._send_mail_to_petition_supporters(
            'iris-petition-loser-notification-for-supporters')

    def send_support_won_mail_to_owner(self, **kwargs):
        self.set_response_token()
        self._send_mail_to_petition_owner(
            'iris-petition-processing-notification-for-owner')

    def send_support_won_mail_to_supporters(self, **kwargs):
        self.set_response_token()
        self._send_mail_to_petition_supporters(
            'iris-petition-processing-notification-for-supporters')

    def send_closed_mail_to_owner(self, **kwargs):
        self._send_mail_to_petition_owner('iris-petition-closed')

    def send_closed_mail_to_supporters(self, **kwargs):
        self._send_mail_to_petition_supporters(
            'iris-petition-closed-notification-for-supporters')

    def _send_mail_to_petition_owner(self, template):
        return self._send_mail(template,
                               [self.petition.owner.relation_dict])

    def _send_mail_to_petition_supporters(self, template):
        owner_id = self.petition.owner.id
        to = [s.user.relation_dict
              for s in self.petition.get_supporters()
              if s.user.id != owner_id
             ]
        return self._send_mail(template, to)

    def _send_mail(self, template, to):
        """Send a petition mail

        `to` is checked if the email provided is trusted. Untrusted entries
        are removed.
        """
        rcpt = [r for r in to if r.get('email_trusted', False)]
        if not rcpt:
            return None
        return send_petition_mail(
            self.request,
            template,
            self.petition,
            rcpt,
        )


HIDDEN_TRIGGERS = [
    'check',
    'tick',
    'reset',
    'support',
    'publish',
    'reset_support_start_time',
]


def fromYAML(raw=False):
    """Get state machine configuration from a yml file

    raw=false: result is modified so that it can be used with the transitions
               package
    raw=true: result is provided as is to be used in the API

    HIDDEN_TRIGGERS are removed when raw == true
    """
    data = {}
    filename = os.path.join(os.path.dirname(__file__), 'states.yaml')
    with open(filename, 'r') as yamlFile:
        data = yaml.load(yamlFile.read())

    transitions = data.setdefault('transitions', [])
    if raw:
        # The raw version provides the states with all transitions assigned.
        def insert(transition, states, baseName=None):
            # insert a transitions into the states
            source = transition.get('source')
            if not source:
                return
            tr = copy.deepcopy(transition)
            del tr['source']
            for state in states:
                name = state['name']
                if baseName is not None:
                    name = baseName + NestedState.separator + name
                if source == '*' or source == state['name']:
                    trs = state.setdefault('transitions', [])
                    trs.append(tr)
                if 'children' in state:
                    insert(transition, state['children'], name)
        # insert globally defined transitions into the states
        states = data.get('states', [])
        for tr in transitions:
            insert(tr, states)

        def remove_hidden_triggers(state):
            transitions = state.get('transitions', [])
            for transition in list(transitions):
                if transition['trigger'] in HIDDEN_TRIGGERS:
                    transitions.remove(transition)
            if 'children' in state:
                for child_state in state['children']:
                    remove_hidden_triggers(child_state)
        for state in states:
            remove_hidden_triggers(state)
        return data

    # prepare the data to be able to use it for the state machine
    def extractTransitions(state, parentName=None):
        if isinstance(state, list):
            for s in state:
                extractTransitions(s)
        else:
            name = state['name']
            if parentName:
                name = parentName + NestedState.separator + name
            if 'transitions' in state:
                for transition in state['transitions']:
                    transition['source'] = name
                    transitions.append(transition)
                del state['transitions']
            if 'children' in state:
                for s in state['children']:
                    extractTransitions(s, name)
    extractTransitions(data.get('states', []))
    return data


def includeme(config):
    global APPROVAL_DAYS, BEFORE_LOSER_DAYS, LETTER_WAIT_DAYS, SMS_VERIFICATION
    settings = config.get_settings()
    APPROVAL_DAYS = int(settings['iris.approval.days'])
    BEFORE_LOSER_DAYS = int(settings.get('iris.beforeloser.days', '2'))
    LETTER_WAIT_DAYS = int(settings['iris.letter.wait.days'])
    SMS_VERIFICATION = settings.get('iris.sms.verification',
                                    'true'
                                   ).lower() == 'true'
    config.add_view(
        condition_error_request_handler,
        renderer='json',
        context=ConditionError,
        http_cache=0,
    )
