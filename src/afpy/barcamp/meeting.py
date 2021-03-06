"""This module allows to define and manage meetings
"""
from afpy.barcamp.app import AfpyBarcamp
from afpy.barcamp.authentication import setup_authentication
from afpy.barcamp.duration import Durations, IDurations
from afpy.barcamp.interfaces import ISeanceContainer
from afpy.barcamp.people import IPeopleContainer, PeopleContainer
from afpy.barcamp.registration import IRegistrable
from afpy.barcamp.room import Rooms, IRooms
from afpy.barcamp.seance import SeanceContainer
from grokcore import formlib
from z3c.flashmessage.sources import SessionMessageSource
from zope.app.authentication.authentication import PluggableAuthentication
from zope.app.container.interfaces import IContainer, IContained
from zope.app.security.interfaces import IAuthentication
from zope.component import getUtility
from zope.interface import implements
from zope.schema import Datetime, TextLine, Text
import grok
import megrok.menu
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('afpy.barcamp')

class IMeeting(IContainer, IContained):
    """interface of an meeting
    """
    name = TextLine(title=_(u'Display name'))
    address = TextLine(title=_(u'Address'), required=False)
    start_date = Datetime(title=_(u'Start date'), required=False)
    end_date = Datetime(title=_(u'End date'), required=False)
    headline = TextLine(title=_(u'Headline'), required=False)
    description = Text(title=_(u'Description'), required=False)


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
    grok.local_utility(Rooms,
                       public=True,
                       provides=IRooms,
                       name_in_container='rooms')


class ManageMeetingsPermission(grok.Permission):
    grok.name('afpy.barcamp.managemeetings')
    grok.title(_(u'Manage Meetings')) # optional


def start_date_sort(a, b):
    if a.start_date is None:
        return 1
    if b.start_date is None:
        return -1
    return cmp(a.start_date, b.start_date)

class Index(formlib.DisplayForm):
    """view of the meeting
    """
    form_fields = grok.AutoFields(IMeeting)
    megrok.menu.menuitem(menu='actions')
    grok.title(_(u'View'))

    def update(self):
        self.sorted_seances = list(
            getUtility(ISeanceContainer,
                       context=grok.getSite()).values())
        self.sorted_seances.sort(start_date_sort)
        super(Index, self).update()


class Add(formlib.AddForm):
    grok.require('afpy.barcamp.managemeetings')
    grok.context(AfpyBarcamp)
    form_fields = grok.AutoFields(IMeeting)
    megrok.menu.menuitem(menu='actions')
    grok.title(_(u'Add a meeting'))

    def update(self):
        self.form_fields['__name__'].field.title = _(u'URL name')
        super(Add, self).update()

    def setUpWidgets(self, ignore_request = False):
        super(Add, self).setUpWidgets(ignore_request)

    @formlib.action(_(u'Add meeting'))
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
    grok.title(_(u'Edit'))

    @formlib.action(_(u'Apply'))
    def apply(self, **data):
        self.applyData(self.context, **data)
        self.redirect(self.url('index'))

class Upgrade(grok.View):
    """Allows to upgrade the meeting object
    This was added to be able to add the Room utility
    after the meeting object was created
    """
    grok.require('afpy.barcamp.managemeetings')
    megrok.menu.menuitem(menu='actions')
    grok.title(_(u'Upgrade'))
    def update(self):
        # check if we need an upgrade
        self.need_upgrade = False
        if 'rooms' not in self.context.keys():
            self.need_upgrade = True
        # do the upgrade if asked
        if 'do_upgrade' in self.request:
            # UPGRADE
            self.context['rooms'] = rooms = Rooms()
            sm = grok.getSite().getSiteManager()
            sm.registerUtility(rooms, IRooms)
            SessionMessageSource().send(_(u'Database successfully upgraded!'))


