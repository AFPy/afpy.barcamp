"""This module defines all the needed elements to handle registration.
The registration concept we have developped is working for any kind of resources
Seances and Meetings, the only condition is to implement IRegistrable. Once your
resource implements IRegistrable it can use our registration component to
provide the user/visitor registration.

"""

# our own application imports
from afpy.barcamp.interfaces import ISideBar
from afpy.barcamp.people import People, IPeopleContainer
from afpy.barcamp.interfaces import IRegistrable, IRegistration

# zope & co
from z3c.flashmessage.sources import SessionMessageSource
from zope.component import getUtility
from zope.interface import Interface
from zope.security.interfaces import Unauthorized
from zope.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.session.interfaces import ISession

# grok
import grok

class RegistrationPermission(grok.Permission):
    grok.name('afpy.barcamp.register')
    grok.title('Can register') # optional


class RegistrationPage(grok.View):
    """Page to register to a seance or meeting, and used for the UI.
    """
    grok.require('afpy.barcamp.register') # TODO zope.authenticated?
    grok.context(IRegistrable)
    registered = False
    nick = None

    def update(self):
        if IRegistration(self.context).is_registered(nick):
            self.prompt = u'You are already registered'
            self.registered = True


class RegistrationViewlet(grok.Viewlet):
    """viewlet that offers (un)registration UI for IRegistrable objects
    """
    grok.context(IRegistrable)
    grok.viewletmanager(ISideBar)
    registered = loggedin = False
    nick = None

    def update(self):
        if IRegistration(self.context).is_registered(nick):
            self.prompt = u'You are already registered'
            self.registered = True


class Registration(grok.View):
    """view that really does the (un)registration
    but is independent from any rendering or template
    """
    grok.context(IRegistrable)
    grok.traversable('register') # allows to access @@registration/register
    grok.traversable('unregister')

    def update(self):
        self.nick  = self.request.principal.id
        if 'unregister' in self.request:
            self.unregister()

        if 'register' in self.request:
            self.register()

    def render(self):
        pass

    def register(self):
        # do the registration
        IRegistration(self.context).register(self.nick)
        # grant permission to add a seance
        IPrincipalPermissionManager(grok.getSite()).grantPermissionToPrincipal('afpy.barcamp.addseance',
                                                                               self.nick)
        # store the nick in the session
        # TODO should be removed since we use auth
        ISession(self.request)['afpy.barcamp']['nick'] = self.nick
        # Display a message for the next page
        msg = (u'You have been added to %s!' % self.context.name)
        SessionMessageSource().send(msg)
        self.redirect(self.url(''))

    def unregister(self):
        if IRegistration(self.context).is_registered(self.nick):
            # unregister the person
            IRegistration(self.context).unregister(self.nick)
            # remove the permission
            IPrincipalPermissionManager(grok.getSite()).unsetPermissionForPrincipal('afpy.barcamp.addseance',
                                                                                    self.nick)
            # display a message on the next screen
            msg = (u'You have been removed from %s!'
                   % self.context.name)
            SessionMessageSource().send(msg)
            self.redirect(self.url(''))
