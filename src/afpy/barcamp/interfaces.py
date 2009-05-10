from afpy.barcamp.duration import DurationSource
from afpy.barcamp.room import RoomSource
from zope.app.container.interfaces import IContainer
from zope.interface import Interface, Attribute
from zope.schema import Datetime, TextLine, Text, Choice
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('afpy.barcamp')

class ISideBar(Interface):
    """marker interface of the sidebar
    """


class IRegistrable(Interface):
    """marker interface to let seances and meetings support registration
    """


class IRegistration(Interface):
    """Interface to get or set the registration status
    if a registrable object (meeting or seance)
    """
    def is_registered(nick):
        """returns True if the nick is registered
        for this object (meeting or seance)
        """

    def register(nick):
        """register the nick for the meeting or seance
        """

    def unregister(nick):
        """unregister the nick for the meeting or seance
        """

    def everybody():
        """returns an iterable of registered people
        """

class ISeanceContainer(IContainer):
    pass


class ISeance(IContainer):
    """interface of a seance
    """
    name = TextLine(title=_(u'Title of the session'))
    start_date = Datetime(title=_(u'Date and time'), required=False)
    duration = Choice(title=_(u'Type'), source=DurationSource())
    room = Choice(title=_(u'Room'), source=RoomSource())
    description = Text(title=_(u'Description'), required=False)
    keywords = TextLine(title=_(u'Keywords'),
                        description=_(
                u'Keywords describing your session, separated by a comma.'),
                        required=False)
    audience = Choice(title=_(u'Audience'), # TODO configurable source
                    values=('Debutant', 'Intermediaire', 'Avance', 'Tous niveaux'))
    authors = Attribute(_(u'Name of persons leading the session'))
    status = Choice(title=_(u'Statut'), values=('proposed', 'confirmed', 'cancelled'))
    unfolding = Text(title=_(u'Unfolding of the session'), required=False)
    benefits = Text(title=_(u'Benefits for attendees'), required=False)


