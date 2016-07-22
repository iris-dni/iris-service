

class StateMachine(object):

    TRANSITIONS = {}

    def __init__(self, currentState):
        self.current = currentState

    def switch(self, transitionName):
        tr = self.TRANSITIONS.get(self.current, {})
        self.current = tr.get(transitionName)
        return self.current
