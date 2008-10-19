from zope.app.container.interfaces import IContainer
from zope.interface import Interface, implements
from zope.schema import TextLine
import grok

class IPeople(IContainer):
    """interface of a people"""
    
    name = TextLine(title=u'name')


class People(grok.Container):
    """the person that is supposed to make a presentation"""

    implements(IPeople)

    def __init__(self, name):
        super(People, self).__init__()
        self.name = name


class Index(grok.View):
    """the view of the person"""

    def render(self): pass
