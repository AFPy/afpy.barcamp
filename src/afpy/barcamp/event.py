from afpy.barcamp.people import PeopleContainer
from grokcore import formlib
from afpy.barcamp.session import SessionContainer
from zope.app.container.interfaces import IContainer
from zope.app.folder import Folder
from zope.interface import implements, Interface
from zope.schema import Datetime, TextLine
import grok

class IEvent(IContainer):
    """interface of an event
    """
    name = TextLine(title=u'name')
    address = TextLine(title=u'address')
    start_date = Datetime(title=u'start date')
    end_date = Datetime(title=u'end date')


class Event(grok.Container):
    """the event itself
    """
    implements(IEvent)
    name = address = start_date = end_date = None

    def __init__(self, name=None):
        super(Event, self).__init__()
        self.name = name
        self['sessions'] = SessionContainer()
        self['people'] = PeopleContainer()


class Index(formlib.DisplayForm):
    """view of the event
    """
    form_fields = grok.AutoFields(IEvent)


class EditEvent(formlib.EditForm):
    """view to edit the event
    """
    form_fields = grok.AutoFields(IEvent)

    @formlib.action('Apply')
    def apply(self, **data):
        self.applyData(self.context, **data)
        self.redirect(self.url('index'))





