from afpy.barcamp.authentication import setup_toplevel_authentication
from afpy.barcamp.interfaces import ISideBar
from grokcore import formlib
from megrok.menu import Menu
from zope.app.authentication.authentication import PluggableAuthentication
from zope.app.container.browser.contents import Contents
from zope.app.security.interfaces import IAuthentication
from zope.interface import Interface, implements
import grok
import megrok.menu
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('afpy.barcamp')

class AfpyBarcamp(grok.Application, grok.Container):
    """The main application container
    """
    grok.local_utility(PluggableAuthentication,
                       provides=IAuthentication,
                       setup=setup_toplevel_authentication)


class Index(Contents, grok.View):
    megrok.menu.menuitem('actions')
    grok.title(_(u'View'))


class Edit(Contents, grok.View):
    grok.require('zope.ManageContent')
    megrok.menu.menuitem('actions')
    grok.title(_(u'Edit'))
    # see app_templates/edit.pt


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


class Navigation(Menu):
    """main navigation menu
    """
    grok.name('navigation')
    grok.title(_(u'Navigation menu'))
    grok.description('')


class Actions(Menu):
    """context actions menu
    """
    grok.name('actions')
    grok.title(_(u'Actions menu'))
    grok.description('')


