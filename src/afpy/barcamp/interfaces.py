from zope.app.container.interfaces import IContainer
from zope.interface import Interface
from zope.interface import Attribute
from zope.schema import Datetime, TextLine

class ISideBar(Interface):
    """marker interface of the sidebar
    """


class IRegistrable(Interface):
    """marker interface to let sessions and events support registration
    """


class ISessionContainer(IContainer):
    pass


class ISession(IContainer):
    """interface of a session
    """
    name = TextLine(title=u'name')
    date = Datetime(title=u'date', required=False)
    nicknames = Attribute(u'names of persons attending the session')


