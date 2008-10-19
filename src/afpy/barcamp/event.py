from zope.app.container.interfaces import IContainer
from zope.interface import implements, Interface
from zope.schema import Datetime, TextLine
from zope.app.folder import Folder
import grok

class IEvent(IContainer):
    """interface of an event"""

    name = TextLine(title=u'name')
    address = TextLine(title=u'address')
    start_date = Datetime(title=u'start date')
    end_date = Datetime(title=u'end date')


class Event(grok.Container):
    """the event itself"""

    implements(IEvent)
    name = address = start_date = end_date = None

    def __init__(self, name=None):
        super(Event, self).__init__()
        self.name = name
        self['sessions'] = Folder()
        self['people'] = Folder()


class Index(grok.DisplayForm):
    """view of the event"""
    form_fields = grok.AutoFields(IEvent)

class EditEvent(grok.EditForm):
    """view to edit the event"""
    form_fields = grok.AutoFields(IEvent)

    @grok.action('Apply')
    def apply(self, **data):
        self.applyData(self.context, **data)
        self.redirect(self.url('index'))





