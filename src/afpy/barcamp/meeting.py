from afpy.barcamp.authentication import setup_authentication
from zope.app.authentication.authentication import PluggableAuthentication
from zope.app.security.interfaces import IAuthentication
from afpy.barcamp.people import IPeopleContainer
from afpy.barcamp.people import PeopleContainer
from afpy.barcamp.seance import ISeanceContainer
from afpy.barcamp.seance import SeanceContainer
from grokcore import formlib
from zope.app.container.interfaces import IContainer
from zope.app.folder import Folder
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
    implements(IMeeting)
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



