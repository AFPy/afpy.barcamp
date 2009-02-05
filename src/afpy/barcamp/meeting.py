from afpy.barcamp.authentication import setup_authentication
from afpy.barcamp.interfaces import IRegistration
from afpy.barcamp.people import IPeopleContainer
from afpy.barcamp.people import PeopleContainer
from afpy.barcamp.registration import IRegistrable
from afpy.barcamp.seance import ISeanceContainer
from afpy.barcamp.seance import SeanceContainer
from grokcore import formlib
from zope.app.authentication.authentication import PluggableAuthentication
from zope.app.container.interfaces import IContainer
from zope.app.folder import Folder
from zope.app.security.interfaces import IAuthentication
from zope.component import adapts
from zope.interface import implements, Interface
from zope.schema import Datetime, TextLine
import grok

class IMeeting(IContainer):
    """interface of an meeting
    """
    name = TextLine(title=u'name')
    address = TextLine(title=u'address', required=False)
    start_date = Datetime(title=u'start date', required=False)
    end_date = Datetime(title=u'end date', required=False)
    date_label = TextLine(title=u"date label", required=False)


class Meeting(grok.Container, grok.Site):
    """the meeting itself
    """
    implements(IMeeting, IRegistrable)
    name = address = start_date = end_date = date_label = None
    grok.local_utility(PluggableAuthentication,
                       provides=IAuthentication,
                       setup=setup_authentication)
    grok.local_utility(SeanceContainer,
                       public=True,
                       provides=ISeanceContainer,
                       name_in_container='seances')
    grok.local_utility(PeopleContainer,
                       public=True,
                       provides=IPeopleContainer,
                       name_in_container='people')

    def __init__(self):
        self.nicknames = set()
        super(Meeting, self).__init__()


class MeetingRegistration(grok.Adapter):
    grok.provides(IRegistration)
    grok.context(IMeeting)

    def __init__(self, context):
        self.context = context

    def is_registered(self, nick):
        return nick in self.context.nicknames

    def register(self, nick):
        self.context.nicknames.add(nick)

    def unregister(self, nick):
        if not self.is_registered(nick):
            self.context.remove(nick)

    def everybody(self):
        return self.context.nicknames


class Index(formlib.DisplayForm):
    """view of the meeting
    """
    form_fields = grok.AutoFields(IMeeting)


class Edit(formlib.EditForm):
    """view to edit the meeting
    """
    form_fields = grok.AutoFields(IMeeting)

    @formlib.action('Apply')
    def apply(self, **data):
        self.applyData(self.context, **data)
        self.redirect(self.url('index'))



