import copy
import jsonpickle

from lovely.esdb.document import Document
from lovely.esdb.properties import Property, ObjectProperty
from lovely.essequence import Sequence

from transitions.extensions.nesting import NestedState

from ..db.dc import dc_defaults_all


# IID generator to create the integer ids for petitions
IID = Sequence('petitions').next


class Petition(Document):

    INDEX = 'petitions'

    id = Property(primary_key=True, default=IID)

    dc = Property(
        default=dc_defaults_all(),
        doc="Dublin Core data."
    )

    state = ObjectProperty(
        default=lambda: StateContainer(name='draft',
                                       parent='',
                                       listable=False,
                                       timer=0),
        doc="""
          The current state information of the petition.
          The state is controlled via a state machine.
        """
    )

    tags = Property(
        default=lambda: [],
        doc="""
          A list of tags which are searchable.
        """,
    )

    title = Property(
        default=''
    )

    city = Property(
        default=None,
        doc="""
          A reference to a city (id).
        """
    )

    city_answer = Property(
        default='',
        doc="""
          The answer provided by the city authority
        """
    )

    type = Property(
        default='',
        doc="""
          A string defined by the frontend (no internal meaning).
        """
    )

    description = Property(
        default=''
    )

    suggested_solution = Property(
        default=''
    )

    images = Property(
        default=[],
        doc="A list of file ids."
    )

    links = Property(
        default=lambda: [],
        doc="A list of location ids."
    )

    videos = Property(
        default=lambda: [],
        doc="A list of location ids to youtube videos."
    )

    connected_locations = Property(
        default=lambda: [],
        doc="""
          A list of location ids to location which are connected to this
          petition.
        """
    )

    supporters = Property(
        default=lambda: {
            "amount": 0,
            "required": 0,
        },
        doc="""
          An object which contains information about the supporters of the
          petition.
        """
    )

    owner = Property(
        default=None
    )

    response_token = Property(
        default=None
    )

    def __repr__(self):
        return "<%s [id=%r]>" % (self.__class__.__name__, self.id)


class StateContainer(object):

    def __init__(self,
                 name='draft',
                 parent='',
                 **kwargs):
        self.name = name
        self.parent = parent
        for name, value in kwargs.iteritems():
            if name not in set(['py/object']):
                setattr(self, name, value)

    def get_full_name(self):
        if self.parent:
            return NestedState.separator.join([self.parent,
                                               self.name])
        return self.name

    def set_full_name(self, value):
        states = value.split(NestedState.separator, 1)
        self.name = states[-1]
        if len(states) > 1:
            self.parent = states[0]
        else:
            self.parent = Petition.state.default().parent

    full_name = property(get_full_name, set_full_name)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__,
                            self.full_name)


class StateContainerJSONPickleHandler(jsonpickle.handlers.DatetimeHandler):
    """JSON Pickle handler for the StateContainer
    """

    def flatten(self, obj, data):
        """Provides the StateContainer __dict__ as payload
        """
        payload = obj.__dict__
        if not self.context.unpicklable:
            return copy.copy(payload)
        data.update(payload)
        return data

    def restore(self, data):
        return StateContainer(**data)

StateContainerJSONPickleHandler.handles(StateContainer)
