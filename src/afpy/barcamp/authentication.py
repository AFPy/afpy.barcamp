"""This module offers authentication for afpy.barcamp
"""
from afpy.barcamp.people import IPeople, IPeopleContainer
from zope.sendmail.interfaces import IMailDelivery
from afpy.barcamp.people import People
from md5 import md5
from random import choice
from zope import schema
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.app.authentication.interfaces import ICredentialsPlugin
from zope.app.authentication.interfaces import IPrincipalInfo
from zope.app.authentication.session import SessionCredentialsPlugin
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import ILogout
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.component import getUtility
from zope.interface import Interface
from zope.securitypolicy.interfaces import IPrincipalPermissionManager
import grok


def setup_toplevel_authentication(pau):
    """Set up pluggable authentication utility
    at application level, so that we can manage meetings

    Sets up an IAuthenticatorPlugin and
    ICredentialsPlugin (for the authentication mechanism)
    """
    pau.credentialsPlugins = ['credentials']
    pau.authenticatorPlugins = ['app_admin']


def setup_authentication(pau):
    """Set up pluggable authentication utility
    at Meeting level, so that authentication is different for each Meeting.

    Sets up an IAuthenticatorPlugin and
    ICredentialsPlugin (for the authentication mechanism)
    """
    pau.credentialsPlugins = ['credentials']
    pau.authenticatorPlugins = ['meeting_admin']


class MySessionCredentialsPlugin(grok.GlobalUtility, SessionCredentialsPlugin):
    """credentials plugin for the PluggableAuthentication
    """
    grok.provides(ICredentialsPlugin)
    grok.name('credentials')

    loginpagename = 'login'
    loginfield = 'form.login'
    passwordfield = 'form.password'


class PrincipalInfo(object):
    """object to be returned by the authenticator plugin
    """
    grok.implements(IPrincipalInfo)

    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description
        self.credentialsPlugin = None
        self.authenticatorPlugin = None


class ToplevelAuthenticatorPlugin(grok.GlobalUtility):
    """toplevel authentication plugin for the PluggableAuthentication
    used at the application level, to manage meetings
    """
    grok.provides(IAuthenticatorPlugin)
    grok.name('app_admin')

    def authenticateCredentials(self, credentials):
        if not isinstance(credentials, dict):
            return None
        if not ('login' in credentials and 'password' in credentials):
            return None
        # hardcoded admin account
        if credentials['login'] != 'admin' and credentials['password'] != 'barcamp':
            return None
        # grant permission to the hardcoded admin
        IPrincipalPermissionManager(grok.getSite()).grantPermissionToPrincipal ('zope.ManageContent', 'admin')
        return PrincipalInfo(id='admin',
                             title='admin',
                             description='admin')

    def principalInfo(self, id):
        return PrincipalInfo(id='admin',
                             title='admin',
                             description='admin')


class UserAuthenticatorPlugin(grok.GlobalUtility):
    """authentication plugin for the PluggableAuthentication
    used at the meeting, to manage seances
    """
    grok.provides(IAuthenticatorPlugin)
    grok.name('meeting_admin')

    def authenticateCredentials(self, credentials):
        if not isinstance(credentials, dict):
            return None
        if not 'login' in credentials or not 'password' in credentials:
            return None
        username = credentials.get('login')
        password = credentials.get('password')
        if username is None or password is None:
            return None
        peoplelist = getUtility(IPeopleContainer, context=grok.getSite())
        people = peoplelist.get(username)
        if people is None:
            return None
        if md5(people.password or '').digest() != md5(credentials['password']):
            return None
        return PrincipalInfo(id=people.name,
                             title=people.name,
                             description=people.name)

    def principalInfo(self, id):
        people = self.getPeople(id)
        if people is None:
            return None
        return PrincipalInfo(id=people.name,
                             title=people.name,
                             description=people.name)

    def getPeople(self, id):
        return getUtility(IPeopleContainer, context=grok.getSite()).get(id)


class ILoginForm(Interface):
    login = schema.BytesLine(title=u'Username', required=True)
    password = schema.Password(title=u'Password', required=True)


class Login(grok.Form):
    """View for the login form
    """
    grok.context(Interface)
    grok.require('zope.Public')

    form_fields = grok.Fields(ILoginForm)

    def update(self):
        super(Login, self).update()

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
            auth = getUtility(IAuthentication)
            ILogout(auth).logout(self.request)

    def render(self):
        self.redirect(self.request.form.get('camefrom', ''))


class SignIn(grok.Form):
    """View for the sign-in form
    """
    grok.context(Interface)
    grok.require('zope.Public')

    form_fields = grok.Fields(IPeople).omit('password')

    def update(self):
        super(SignIn, self).update()

    @grok.action('sign in')
    def handle_signin(self, **data):
        """signin button and signin action
        """
        # create the people
        people = People()
        self.applyData(people, **data)
        # check the login is not taken
        # TODO
        # generate a nice but weak password
        password = u''.join(
            [choice(['z','r','t','p','q',
                     's','d','f','g','h',
                     'j','k','l','m','w',
                     'x','c','v','b','n'])
            + choice(['a','e','i','o','u','y'])
            for i in range(4)])
        people.password = md5(password).digest()
        email = u'''You can connect to %s

        With the following informations:

        login : %s
        password : %s''' % (grok.getSite().__name__,
                            people.name,
                            password)
        mailer = getUtility(IMailDelivery, 'afpy.barcamp')
        mailer.send('contact@afpy.org', people.email, email)
        self.redirect('login?check_your_mail')


