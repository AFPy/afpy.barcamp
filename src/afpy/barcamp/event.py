import grok
from zope.schema import Datetime, TextLine
from zope.interface import implements, Interface

class IEvent(Interface):

    name = TextLine(title=u'name')
    address = TextLine(title=u'address')
    start_date = Datetime(title=u'start date')
    end_date = Datetime(title=u'end date')


class Event(grok.Container):
    """the event itself"""
    implements(IEvent)

    def __init__(self, name, address, start_date, end_date):
        super(Event, self).__init__()
        self.name = name
        self.address = address
        self.start_date = start_date
        self.end_date = end_date

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
