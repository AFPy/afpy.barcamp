from afpy.barcamp.authentication import setup_toplevel_authentication
from afpy.barcamp.meeting import IMeeting, Meeting
from afpy.barcamp.interfaces import ISideBar
from grokcore import formlib
from zope.app.authentication.authentication import PluggableAuthentication
from zope.app.container.browser.contents import Contents
from zope.app.security.interfaces import IAuthentication
from zope.interface import Interface, implements
import grok


class AfpyBarcamp(grok.Application, grok.Container):
    """The main application container
    """
    grok.local_utility(PluggableAuthentication,
                       provides=IAuthentication,
                       setup=setup_toplevel_authentication)


class Index(Contents, grok.View):
    pass # see app_templates/index.pt


class Edit(Contents, grok.View):
    grok.require('zope.ManageContent')
    # see app_templates/edit.pt


class AddMeeting(formlib.AddForm):
    grok.require('zope.ManageContent')
    grok.context(AfpyBarcamp)
    form_fields = grok.AutoFields(IMeeting)

    def setUpWidgets(self, ignore_request = False):
        super(AddMeeting, self).setUpWidgets(ignore_request)

    @formlib.action('Add meeting')
    def add(self, **data):
        obj = Meeting()
        self.applyData(obj, **data)
        # TODO generate a correct blurb that removes accents
        name = data['name'].lower().replace(' ', '_')
        self.context[name] = obj
        self.redirect(self.url('index'))


class BarcampToplevelMacros(grok.View):
    """The view providing the global macros for view upper than meeting level
    """
    grok.context(Interface)


class BarcampMacros(grok.View):
    """The view providing the global macros for meeting under the meeting level
    """
    grok.context(Interface)


class SideBar(grok.ViewletManager):
    """a viewlet manager used to hold some viewlets.
    It can be used as a sidebar
    """
    implements(ISideBar)
    grok.name('sidebar')
    grok.view(Interface)
    grok.context(Interface)



