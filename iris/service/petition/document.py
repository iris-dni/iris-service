import copy
import jsonpickle
import transitions

from lovely.esdb.document import Document
from lovely.esdb.properties import (
    Property,
    ObjectProperty,
    LocalRelation,
    LocalOne2NRelation,
)
from lovely.essequence import Sequence

from transitions.extensions.nesting import NestedState

from ..db.dc import dc_defaults, dc_defaults_all, DC_CREATED

from .sm import PetitionStateMachine


# IID generators to create the integer ids for the documents
PETITIONS_IID = Sequence('petitions').next


class Petition(Document):

    INDEX = 'petitions'

    id = Property(primary_key=True, default=PETITIONS_IID)

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

    city = LocalRelation(
        '_relations.city',
        'City.id',
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

    images = LocalOne2NRelation(
        '_relations.images',
        'File.id',
        relationProperties={
            'state': 'visible'
        },
        doc="An image list for the petition."
    )

    videos = LocalOne2NRelation(
        '_relations.videos',
        'WebLocation.id',
        relationProperties={
            'state': 'visible'
        },
        doc="A list of  web locations to youtube videos."
    )

    links = LocalOne2NRelation(
        '_relations.links',
        'WebLocation.id',
        relationProperties={
            'state': 'visible'
        },
        doc="A list of web locations with links for the petition."
    )

    connected_locations = LocalOne2NRelation(
        '_relations.connected_locations',
        'WebLocation.id',
        relationProperties={
            'state': 'visible'
        },
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

    owner = LocalRelation(
        '_relations.owner',
        'User.id',
        doc="""
          The owner of the petition.
        """
    )

    response_token = Property(
        default=None
    )

    _relations = Property(
        name="relations",
        default=lambda: {
            "images": [],
            "videos": [],
            "links": [],
            "connected_locations": []
        },
        doc="""
          The petition relations.
        """
    )

    def addSupporter(self, user=None, phone_user=None):
        """Add a supporter to the petition

        Update the supporters amount.

        The phone_user object must provide at least a 'telephone' property.

        returns the supporter document
        """
        if user is not None:
            supporter = 'u:%s' % user
        else:
            supporter = 't:%s' % phone_user['telephone']
        supporterId = '%s-%s' % (self.id, supporter)
        supporter = Supporter.get(supporterId)
        if supporter is None:
            supporter = Supporter(
                id=supporterId,
                petition=self.id,
                user=user,
                phone_user=phone_user
            )
            self.supporters['amount'] += 1
            try:
                self.sm.check()
            except transitions.MachineError:
                pass
            self.store(refresh=True)
            supporter.store(refresh=True)
        return supporter

    def removeSupporter(self, supporterId):
        """Remove a supporter from the petition

        Update the supporters amount.
        """
        supporter = Supporter.get(supporterId)
        if supporter is not None:
            if self.supporters['amount'] > 0:
                self.supporters['amount'] -= 1
            supporter.delete(refresh=True)
            self.store(refresh=True)

    @property
    def sm(self):
        return PetitionStateMachine(self, None)

    def __repr__(self):
        return "<%s [id=%r]>" % (self.__class__.__name__, self.id)


class Supporter(Document):
    """The supporters for the petitions

    The supporter instances must be manipulated using the methods on the
    petition document implementation.
    """

    INDEX = 'supporters'

    id = Property(
        primary_key=True,
        doc="""
          The id is created from the petition id and the user or telephone
          number (see Petition.addSupporter).
        """
    )

    dc = Property(
        default=dc_defaults(DC_CREATED),
        doc="Dublin Core data."
    )

    petition = LocalRelation(
        '_relations.petition',
        'Petition.id',
        doc="Relation to the petition"
    )

    user = LocalRelation(
        '_relations.user',
        'User.id',
        doc="""
          Relation to the supporting user.
          Not required if the user was identified with a telephone number.
        """
    )

    phone_user = Property(
        default=None,
        doc="""
          A user which was identified via a telephone number.
          This is stored as an object.
        """
    )

    _relations = Property(
        name="relations",
        default=lambda: {},
        doc="""
          The petition relations.
        """
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
