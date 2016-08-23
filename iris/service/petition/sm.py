import copy
import time
import yaml
import os

from transitions.extensions import MachineFactory
from transitions.extensions.nesting import NestedState

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

    def listable(self, **kwargs):
        self.petition.state.listable = True

    def not_listable(self, **kwargs):
        self.petition.state.listable = False

    def reset_timer(self, **kwargs):
        self.petition.state.timer = int(time.time())

    def support_petition(self, **kwargs):
        user = self.request.user
        if user is not None:
            user = user.id
        self.petition.addSupporter(user=user,
                                   **kwargs.get('data', {}))

    def send_rejected_mail_to_owner(self, **kwargs):
        pass

    def send_winner_mail_to_owner(self):
        pass

    def send_approval_request_to_editor(self):
        pass

    def send_approval_notifications(self):
        pass

    def is_support_timeout(self):
        return self.petition.state.timer < (time.time() - APPROVAL_TIME)

    def is_supporter_limit_reached(self):
        supporters = self.petition.supporters
        return supporters['amount'] >= supporters['required']


HIDDEN_TRIGGERS = ['check', 'tick', 'reset']


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
