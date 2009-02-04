from zope.app.container.interfaces import IContainer
from zope.interface import Interface
from zope.interface import Attribute
from zope.schema import Datetime, TextLine, Text

class ISideBar(Interface):
    """marker interface of the sidebar
    """


class IRegistrable(Interface):
    """marker interface to let seances and meetings support registration
    """


class ISeanceContainer(IContainer):
    pass


class ISeance(IContainer):
    """interface of a seance
    """
    name = TextLine(title=u'name')
    date = Datetime(title=u'date', required=False)
    description = Text(title=u'description', required=False)
    author = TextLine(title=u'author')
    nicknames = Attribute(u'names of persons attending the seance')


