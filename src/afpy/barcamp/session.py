from zope.app.container.interfaces import IContainer
from zope.interface import Interface, implements
from zope.schema import TextLine
import grok

class ISession(IContainer):
    """interface of a session"""

    name = TextLine(title=u'name')


class Session(grok.Container):
    """the session (egs a presentation or tutorial"""

    implements(ISession)

    def __init__(self, name):
        self.name = name


class Index(grok.View):
    """the view of the presentation"""

    def render(self): pass
