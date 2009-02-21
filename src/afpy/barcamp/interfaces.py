#coding: utf-8
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
    name = TextLine(title=u'Titre de la séance')
    start_date = Datetime(title=u'Date et heure', required=False)
    duration = Choice(title=u'Type', values=('Lightning Talk (10min)',
                                             'Presentation (20min)',
                                             'Tutoriel (1h)',
                                             'Atelier (2h)'))
    description = Text(title=u'Description', required=False)
    authors = Attribute(u'Noms des personnes qui présentent la séance')
    status = Choice(title=u'statut', values=('proposed', 'confirmed', 'cancelled'))


