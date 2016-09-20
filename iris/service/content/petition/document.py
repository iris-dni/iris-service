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

from transitions.extensions.nesting import NestedState

from iris.service.db.dc import dc_defaults, dc_defaults_all, DC_CREATED
from iris.service.db.sequence import IID_SHORTED

from iris.service.content.weblocation import WebLocation
from iris.service.content.city import document as city_module

from .sm import PetitionStateMachine


class Petition(Document):

    INDEX = 'petitions'

    id = Property(primary_key=True, default=IID_SHORTED)

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

    links = LocalOne2NRelation(
        '_relations.links',
        'WebLocation.id',
        relationProperties={
            'state': 'visible'
        },
        doc="A list of web locations with links for the petition."
    )

    mentions = LocalOne2NRelation(
        '_relations.mentions',
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
            "required": city_module.TRESHOLD_NOT_SET,
        },
        doc="""
          An object which contains information about the supporters of the
          petition.
        """
    )

    owner = LocalRelation(
        '_relations.owner',
        'User.id',
        relationProperties={
            'firstname': '',
            'lastname': '',
            'telephone': '',
            'email': '',
        },
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
            "owner": {},
            "images": [],
            "links": [],
            "mentions": []
        },
        doc="""
          The petition relations.
        """
    )

    def _weblocation_setter(self, value):
        """Set weblocations by url instead of id

        This setter transforms a url property into a web location id for
        LocalOne2NRelation referencing a WebLocation.

        Missing WebLocations are created.
        """
        if not value:
            return value
        urls = {}
        for item in value:
            if isinstance(item, dict) and 'url' in item:
                items = urls.setdefault(item['url'], [])
                items.append(item)
        if urls:
            lookup_urls = sorted(urls.keys())
            locations = WebLocation.mget_urls(lookup_urls)
            for url, location in zip(lookup_urls, locations):
                if location is None:
                    location = WebLocation(url=url)
                    location.store()
                for item in urls[url]:
                    item['id'] = location.id
        return value

    links.setter(_weblocation_setter)
    mentions.setter(_weblocation_setter)

    _city_changed = False

    @city.setter
    def city_setter(self, value):
        """Setting the city needs an update of the required supporters
        """
        self._city_changed = True
        return value

    def store(self, *args, **kwargs):
        if self._city_changed:
            city = self.city()
            if city is None:
                # no city defined
                required = city_module.TRESHOLD_NOT_SET
            else:
                required = city.treshold
                if required == city_module.TRESHOLD_NOT_SET:
                    required = city_module.DEFAULT_TRESHOLD
            self.supporters['required'] = required
        return super(Petition, self).store(*args, **kwargs)

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
            supporter.store(refresh=True)
            self.store(refresh=True)
        return supporter

    def removeSupporter(self, supporterId):
        """Remove a supporter from the petition

        Update the supporters amount.
        """
        supporter = Supporter.get(supporterId)
        if supporter is not None:
            if self.supporters['amount'] > 0:
                self.supporters['amount'] -= 1
            self.store(refresh=True)
            supporter.delete(refresh=True)

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
