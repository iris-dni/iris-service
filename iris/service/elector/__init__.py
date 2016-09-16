import time
import uuid

from elasticsearch import exceptions

from lovely.esdb.document import Document
from lovely.esdb.properties import Property


# The duration how long an election is valid
TTL = 30 * 1000  # ms


class Election(Document):
    """The document for elections entries
    """
    INDEX = 'elections'

    id = Property(primary_key=True)
    ident = Property()
    until = Property()

    def __repr__(self):
        return '<%s {id=%r, ident=%r, until=%r}>' % (
            self.__class__.__name__,
            self.id,
            self.ident,
            self.until)


class Elector(object):
    """An elector to manage the election process
    """

    def __init__(self, name):
        self.name = name
        self._election = None
        self.ident = "%i_%i" % (uuid.getnode(), id(self))

    @property
    def is_elected(self):
        """ Determine if this elector is elected

        If this elector is elected try to prolong the current election
        """
        isElected = self.election.ident == self.ident
        if isElected:
            self._prolong()
        return isElected

    @property
    def election(self):
        """Provides the election document

        Creates a new one if it doesn't exists.
        """
        if self._election is None:
            self._election = Election.get(self.name)
            if self._election is None:
                Election(id=self.name,
                         ident=self.ident,
                         until=self.now + TTL,
                        ).store(refresh=True)
                self._election = Election.get(self.name)
        now = self.now
        if self._election.until <= now:
            self._updateElected()
        return self._election

    def _prolong(self):
        """Prolong current election if this instance is elected
        """
        now = self.now
        if (self._election is None
            or self._election.ident != self.ident  # elected?
            or (self._election.until - now) > (TTL / 2)
           ):
            return
        self._updateElected()

    def _updateElected(self):
        """Try to update the current election to become elected
        """
        if self._election is None:
            return
        self._election.ident = self.ident
        self._election.until = self.now + TTL
        version = self._election._meta.get('_version')
        try:
            self._election.store(version=version)
        except exceptions.ConflictError:
            self._election = Election.get(self.name)

    @property
    def now(self):
        return int(time.time() * 1000)
