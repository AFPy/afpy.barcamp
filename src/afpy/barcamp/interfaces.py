from zope.app.container.interfaces import IContainer
from zope.interface import Interface
from zope.interface import Attribute
from zope.schema import Datetime, TextLine, Text, Int, Choice

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
    name = TextLine(title=u'name of the seance')
    start_date = Datetime(title=u'Date and time', required=False)
    duration = Int(title=u'Duration in minutes', required=False)
    description = Text(title=u'description', required=False)
    authors = Attribute(u'names of persons leading the seance')
    status = Choice(title=u'status', values=('draft', 'validated'))


