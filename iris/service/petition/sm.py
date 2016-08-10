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

    def __init__(self, petition):
        self.petition = petition
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

    def listable(self):
        self.petition.state.listable = True

    def not_listable(self):
        self.petition.state.listable = False

    def reset_timer(self):
        self.petition.state.timer = int(time.time())

    def send_rejected_mail_to_owner(self):
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


def fromYAML():
    data = {}
    filename = os.path.join(os.path.dirname(__file__), 'states.yaml')
    with open(filename, 'r') as yamlFile:
        data = yaml.load(yamlFile.read())

    transitions = data.setdefault('transitions', [])

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
