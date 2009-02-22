"""This module allows to define and manage meetings
"""
from afpy.barcamp.app import AfpyBarcamp
from afpy.barcamp.authentication import setup_authentication
from afpy.barcamp.duration import Durations, IDurations
from afpy.barcamp.interfaces import IRegistration
from afpy.barcamp.people import IPeopleContainer, PeopleContainer
from afpy.barcamp.registration import IRegistrable
from afpy.barcamp.seance import ISeanceContainer, SeanceContainer
from grokcore import formlib
from zope.app.authentication.authentication import PluggableAuthentication
from zope.app.container.interfaces import IContainer, IContained
from zope.app.folder import Folder
from zope.app.security.interfaces import IAuthentication
from zope.component import adapts
from zope.interface import implements, Interface
from zope.schema import Datetime, TextLine, Text
import grok
import megrok.menu

class IMeeting(IContainer, IContained):
    """interface of an meeting
    """
    name = TextLine(title=u'Display name')
    address = TextLine(title=u'address', required=False)
    start_date = Datetime(title=u'start date', required=False)
    end_date = Datetime(title=u'end date', required=False)
    headline = TextLine(title=u'headline', required=False)
    description = Text(title=u"description", required=False)


class Meeting(grok.Container, grok.Site):
    """the meeting itself
    """
    implements(IMeeting, IRegistrable)
    name = description = headline = address = None
    start_date = end_date = None
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
    grok.local_utility(Durations,
                       public=True,
                       provides=IDurations,
                       name_in_container='durations')


class ManageMeetingsPermission(grok.Permission):
    grok.name('afpy.barcamp.managemeetings')
    grok.title('Manage Meetings') # optional


class Index(formlib.DisplayForm):
    """view of the meeting
    """
    form_fields = grok.AutoFields(IMeeting)
    megrok.menu.menuitem(menu='actions')
    grok.title(u'View')

    def update(self):
        super(Index, self).update()


class Add(formlib.AddForm):
    grok.require('afpy.barcamp.managemeetings')
    grok.context(AfpyBarcamp)
    form_fields = grok.AutoFields(IMeeting)
    megrok.menu.menuitem(menu='actions')
    grok.title(u'Add a meeting')

    def update(self):
        self.form_fields['__name__'].field.title = u'URL name'
        super(Add, self).update()

    def setUpWidgets(self, ignore_request = False):
        super(Add, self).setUpWidgets(ignore_request)

    @formlib.action('Add meeting')
    def add(self, **data):
        obj = Meeting()
        self.applyData(obj, **data)
        # TODO generate a correct slug that removes accents
        if '__name__' not in data or data['__name__'] is None:
            name = data['name'].lower().replace(' ', '_')
        else:
            name = data['__name__']
        self.context[name] = obj
        self.redirect(self.url('index'))


class Edit(formlib.EditForm):
    """view to edit the meeting
    """
    grok.require('afpy.barcamp.managemeetings')
    form_fields = grok.AutoFields(IMeeting)
    megrok.menu.menuitem(menu='actions')
    grok.title(u'Edit')

    @formlib.action('Apply')
    def apply(self, **data):
        self.applyData(self.context, **data)
        self.redirect(self.url('index'))



