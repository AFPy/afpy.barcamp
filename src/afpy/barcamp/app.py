import grok
from afpy.barcamp.interfaces import ISideBar
from afpy.barcamp.event import IEvent, Event
from zope.interface import implements
from zope.app.container.browser.contents import Contents
from zope.interface import Interface
from grokcore import formlib
from zope.app.authentication.authentication import PluggableAuthentication
from zope.app.authentication.session import SessionCredentialsPlugin
from zope.app.authentication.interfaces import ICredentialsPlugin
from zope import schema
from zope.app.security.interfaces import (IAuthentication,
                                          IUnauthenticatedPrincipal,
                                          ILogout)


def setup_authentication(pau):
    """Set up plugguble authentication utility.

    Sets up an IAuthenticatorPlugin and
    ICredentialsPlugin (for the authentication mechanism)
    """
    pau.credentialsPlugins = ['credentials']
    pau.authenticatorPlugins = ['users']


class MySessionCredentialsPlugin(grok.GlobalUtility, SessionCredentialsPlugin):
    grok.provides(ICredentialsPlugin)
    grok.name('credentials')

    loginpagename = 'login'
    loginfield = 'form.login'
    passwordfield = 'form.password'


class ILoginForm(Interface):
    login = schema.BytesLine(title=u'Username', required=True)
    password = schema.Password(title=u'Password', required=True)


class Login(grok.Form):
    """View for the login form
    """
    grok.context(Interface)
    grok.require('zope.Public')

    form_fields = grok.Fields(ILoginForm)

    @grok.action('login')
    def handle_login(self, **data):
        """login button and login action
        """
        self.redirect(self.request.form.get('camefrom', ''))


class Logout(grok.View):
    """View for logout
    """
    grok.context(Interface)
    grok.require('zope.Public')

    def update(self):
        if not IUnauthenticatedPrincipal.providedBy(self.request.principal):
            auth = component.getUtility(IAuthentication)
            ILogout(auth).logout(self.request)




class AfpyBarcamp(grok.Application, grok.Container):
    """The main application container
    """
    grok.local_utility(PluggableAuthentication,
                       provides=IAuthentication,
                       setup=setup_authentication)


class Index(Contents, grok.View):
    pass # see app_templates/index.pt


class AddEvent(formlib.AddForm):
    grok.context(AfpyBarcamp)
    form_fields = grok.AutoFields(IEvent)

    def setUpWidgets(self, ignore_request = False):
        super(AddEvent, self).setUpWidgets(ignore_request)

    @formlib.action('Add event')
    def add(self, **data):
        obj = Event()
        self.applyData(obj, **data)
        # TODO generate a correct blurb that removes accents
        name = data['name'].lower().replace(' ', '_')
        self.context[name] = obj
        self.redirect(self.url('index'))


class BarcampToplevelMacros(grok.View):
    """The view providing the global macros for view upper than event level
    """
    grok.context(Interface)


class BarcampMacros(grok.View):
    """The view providing the global macros for event under the event level
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



