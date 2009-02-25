from afpy.barcamp.duration import DurationSource
from zope.app.container.interfaces import IContainer
from zope.interface import Interface, Attribute
from zope.schema import Datetime, TextLine, Text, Int, Choice
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
    name = TextLine(title=_(u'Title of the seance'))
    start_date = Datetime(title=_(u'Date and time'), required=False)
    duration = Choice(title=_(u'Type'), source=DurationSource())
    description = Text(title=_(u'Description'), required=False)
    authors = Attribute(_(u'Name of persones leading the seance'))
    status = Choice(title=_(u'Statut'), values=('proposed', 'confirmed', 'cancelled'))


