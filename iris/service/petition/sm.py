from iris.service.sm import StateMachine


class PetitionStateMachine(StateMachine):

    TRANSITIONS = {
        'draft': {
            'publish': 'pending',
            'delete': 'deleted',
        },
        'edit': {
            'publish': 'publish_request',
            'delete': 'deleted',
        },
        'publish_request': {
            'publish': 'pending',
            'delete': 'deleted',
        },
        'pending': {
            'approved': 'active',
            'reject': 'edit',
            'timeout': 'active',
            'delete': 'deleted',
        },
        'active': {
            'delete': 'deleted',
            'timeout': 'loser',
        },
        'winner': {
            'delete': 'deleted',
            'timeout': 'sendLetterRequested',
        },
        'loser': {
            'delete': 'deleted',
        },
        'sendLetterRequested': {
            'sendLetter': 'waitForLetterResponse',
            'delete': 'deleted',
        },
        'waitForLetterResponse': {
            'setFeedback': 'letterResponseArrived',
            'delete': 'deleted',
        },
        'letterResponseArrived': {
            'delete': 'deleted',
            'close': 'closed',
        },
        'closed': {
            'delete': 'deleted',
        },
        'deleted': {
            'reset': 'draft',
        },
    }

    def __init__(self, petition):
        self.petition = petition
        super(PetitionStateMachine, self).__init__(petition.state)
