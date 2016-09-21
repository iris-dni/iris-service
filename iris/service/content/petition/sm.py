import copy
import time
import yaml
import os

import transitions
from transitions.extensions import MachineFactory
from transitions.extensions.nesting import NestedState

from iris.service.db.sequence import IID_SHORTED

from iris.service.content.city.document import TRESHOLD_NOT_SET

# create a state machine implementation from extensions
Machine = MachineFactory.get_predefined(nested=True)
NestedState.separator = '.'


APPROVAL_TIME = 10


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

    def reset_timer(self, **kwargs):
        self.petition.state.timer = int(time.time())

    def support_petition(self, **kwargs):
        if self.request is None:
            return
        user = self.request.user
        if user is not None:
            user = user.id
        self.petition.addSupporter(user=user,
                                   **kwargs.get('data', {}))

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

    def feedback_has_valid_token(self, data, **kwargs):
        return self.petition.response_token == data['token']

    def set_petition_feedback(self, data, **kwargs):
        self.petition.city_answer = data['answer']

    def send_rejected_mail_to_owner(self, **kwargs):
        pass

    def send_winner_mail_to_owner(self, **kwargs):
        pass

    def send_approval_request_to_editor(self, **kwargs):
        pass

    def send_approval_notifications(self, **kwargs):
        pass

    def is_support_timeout(self, **kwargs):
        return self.petition.state.timer < (time.time() - APPROVAL_TIME)

    def is_supporter_limit_reached(self, **kwargs):
        supporters = self.petition.supporters
        required = supporters.get('required')
        if required == TRESHOLD_NOT_SET:
            return False
        return supporters['amount'] >= required


HIDDEN_TRIGGERS = ['check', 'tick', 'reset', 'support']


def fromYAML(raw=False):
    data = {}
    filename = os.path.join(os.path.dirname(__file__), 'states.yaml')
    with open(filename, 'r') as yamlFile:
        data = yaml.load(yamlFile.read())

    transitions = data.setdefault('transitions', [])
    if raw:
        # The raw version provides a states with all transitions assigned.
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
    global APPROVAL_TIME
    settings = config.get_settings()
    APPROVAL_TIME = int(settings['iris.approval.days']) * 86400
