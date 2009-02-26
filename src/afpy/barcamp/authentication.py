"""This module offers authentication for afpy.barcamp
"""
from afpy.barcamp.people import IPeople, IPeopleContainer
from afpy.barcamp.people import People
from random import choice
from z3c.flashmessage.sources import SessionMessageSource
from zope import schema
from zope.app.authentication.generic import NoChallengeCredentialsPlugin
from zope.app.authentication.interfaces import IAuthenticatorPlugin
from zope.app.authentication.interfaces import ICredentialsPlugin
from zope.app.authentication.interfaces import IPrincipalInfo
from zope.app.authentication.session import SessionCredentialsPlugin
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import ILogout
from zope.app.security.interfaces import IUnauthenticatedPrincipal
from zope.component import getUtility, queryUtility
from zope.interface import Interface
from zope.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from zope.sendmail.interfaces import IMailDelivery
from zope.traversing.browser.absoluteurl import absoluteURL
import grok
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('afpy.barcamp')


def setup_toplevel_authentication(pau):
    """Set up pluggable authentication utility
    at application level, so that we can manage meetings

    Sets up an IAuthenticatorPlugin and
    ICredentialsPlugin (for the authentication mechanism)
    """
    pau.credentialsPlugins = ('nochallenge', 'credentials')
    # authenticate only on toplevel
    pau.authenticatorPlugins = ('app_admin',)


def setup_authentication(pau):
    """Set up pluggable authentication utility
    at Meeting level, so that authentication is different for each Meeting.

    Sets up an IAuthenticatorPlugin and
    ICredentialsPlugin (for the authentication mechanism)
    """
    pau.credentialsPlugins = ('nochallenge', 'credentials')
    # authenticate first on toplevel, then on the people list
    pau.authenticatorPlugins = ('app_admin', 'meeting_admin')


class NochallengeIfAuthenticated(grok.GlobalUtility, NoChallengeCredentialsPlugin):
    """prevent from challenging again if the user is already authenticated
    """
    grok.provides(ICredentialsPlugin)
    grok.name('nochallenge')


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
        # hardcoded admin account TODO Arghhh
        if credentials['login'] != 'admin' and credentials['password'] != 'barcamp':
            return None
        # grant permission to the hardcoded admin
        IPrincipalPermissionManager(grok.getSite()).grantPermissionToPrincipal ('zope.ManageContent', 'admin')
        IPrincipalPermissionManager(grok.getSite()).grantPermissionToPrincipal('afpy.barcamp.managemeetings', 'admin')
        IPrincipalPermissionManager(grok.getSite()).grantPermissionToPrincipal ('afpy.barcamp.editseance', 'admin')
        IPrincipalPermissionManager(grok.getSite()).grantPermissionToPrincipal ('afpy.barcamp.seances.list', 'admin')
        return PrincipalInfo(id='admin',
                             title=_(u'admin'),
                             description=_(u'admin'))

    def principalInfo(self, id):
        return PrincipalInfo(id='admin',
                             title=_(u'admin'),
                             description=_(u'admin'))


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
        login = credentials.get('login')
        password = credentials.get('password')
        if login is None or password is None:
            return None
        peoplelist = getUtility(IPeopleContainer, context=grok.getSite())
        people = peoplelist.get(login)
        if people is None:
            return None
        if not people.check_password(password):
            return None
        return PrincipalInfo(id=people.login,
                             title=people.login,
                             description=people.login)

    def principalInfo(self, id):
        people = self.getPeople(id)
        if people is None:
            return None
        return PrincipalInfo(id=people.login,
                             title=people.login,
                             description=people.login)

    def getPeople(self, id):
        return getUtility(IPeopleContainer, context=grok.getSite()).get(id)


class ILoginForm(Interface):
    login = schema.BytesLine(title=_(u'Username'), required=True)
    password = schema.Password(title=_(u'Password'), required=True)


class Login(grok.Form):
    """View for the login form
    """
    grok.context(Interface)

    form_fields = grok.Fields(ILoginForm)

    def update(self):
        super(Login, self).update()

    @grok.action('login')
    def handle_login(self, **data):
        """login button and login action
        """
        self.redirect(self.request.form.get('camefrom', 'index'))


class Logout(grok.View):
    """View for logout
    """
    grok.context(Interface)

    def update(self):
        if not IUnauthenticatedPrincipal.providedBy(self.request.principal):
            auth = getUtility(IAuthentication)
            ILogout(auth).logout(self.request)

    def render(self):
        self.redirect(self.request.form.get('camefrom', 'index'))


class Confirmation(grok.View):
    """confirmation page after sign-in
    """
    grok.context(Interface)


class MemberRole(grok.Role):
    grok.name('afpy.barcamp.Member')
    grok.title(_(u'Member of the meeting')) # optional
    grok.permissions(
        'afpy.barcamp.seances.list',
        'afpy.barcamp.addseance',
        'afpy.barcamp.can_attend')


class SignIn(grok.Form):
    """View for the sign-in form
    """
    grok.context(Interface)

    form_fields = grok.Fields(IPeople).omit('password')

    def update(self):
        super(SignIn, self).update()
        self.peoplelist = queryUtility(IPeopleContainer, context=grok.getSite()) 
        if self.peoplelist is None:
            # there is no people container at the toplevel
            SessionMessageSource().send(_(u'Please choose the meeting first'))
            self.redirect('index')

    @grok.action('sign in')
    def handle_signin(self, **data):
        """signin button and signin action
        """
        # create the people
        people = People()
        self.applyData(people, **data)
        # check the login is not taken
        if people.login in self.peoplelist:

            self.redirect('signin')

        # generate a weak but nice password
        password = u''.join(
            [choice(['z','r','t','p','q',
                     's','d','f','g','h',
                     'j','k','l','m','w',
                     'x','c','v','b','n'])
            + choice(['a','e','i','o','u','y'])
            for i in range(4)])
        people.password = password

        # send an email with the password
        site = grok.getSite()
        email = _(u'''Content-Type: text/plain; charset=UTF-8
Subject: your account for %s

Dear %s %s,

Thanks for your account!
You can connect to %s with the following informations:

%s

     login : %s
     password : %s''')

        url = absoluteURL(site, self.request)

        if ('HTTP_X_FORWARDED_SCHEME' in self.request
        and 'HTTP_X_FORWARDED_SERVER' in self.request):
          url = (self.request['HTTP_X_FORWARDED_SCHEME'] + '://'
               + self.request['HTTP_X_FORWARDED_SERVER'])

        email = translate(email, context=self.request) % (
                            site.name,
                            people.firstname,
                            people.lastname,
                            site.name,
                            url,
                            people.login,
                            password)
        mailer = getUtility(IMailDelivery, 'afpy.barcamp')
        if 'nomail' not in self.request:
            mailer.send('contact@afpy.org', people.email.encode('utf-8'), email.encode('utf-8'))

        # add the user
        self.peoplelist[people.login] = people

        # grant him the Member role
        prm = IPrincipalRoleManager(grok.getSite())
        prm.assignRoleToPrincipal('afpy.barcamp.Member', people.login)

        self.redirect('confirmation')


