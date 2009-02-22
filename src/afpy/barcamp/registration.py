"""This module defines all the needed elements to handle registration.
Seances and Meetings, the only condition is to implement IRegistrable. Once your
The registration concept we have developped is working for any kind of resources
provide the user/visitor registration.
resource implements IRegistrable it can use our registration component to
"""
from afpy.barcamp.interfaces import IRegistrable, IRegistration
from afpy.barcamp.interfaces import ISideBar
from afpy.barcamp.people import People, IPeopleContainer
from z3c.flashmessage.sources import SessionMessageSource
from zope.component import getUtility
from zope.interface import Interface
from zope.security.interfaces import Unauthorized
from zope.securitypolicy.interfaces import IPrincipalPermissionManager
from zope.session.interfaces import ISession
import grok
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('afpy.barcamp')


class RegistrationPermission(grok.Permission):
    grok.name('afpy.barcamp.register')
    grok.title(_(u'Can register')) # optional

class RegistrationPermission(grok.Permission):
    grok.name('afpy.barcamp.can_attend')
    grok.title(_(u'Can attend')) # optional

class Registration(grok.Adapter):
    """generic adapter for registration.
    Used for meetings and seances
    """
    grok.provides(IRegistration)
    grok.context(IRegistrable)

    def __init__(self, context):
        self.context = context
        if not hasattr(self.context, '_nicknames'):
            self.context._nicknames = set()

    def is_registered(self, nick):
        #FIXME use annotations instead
        return nick in self.context._nicknames

    def register(self, nick):
        self.context._nicknames.add(nick)

    def unregister(self, nick):
        if self.is_registered(nick):
            self.context._nicknames.remove(nick)

    def everybody(self):
        return self.context._nicknames


class RegistrationViewlet(grok.Viewlet):
    """viewlet that offers (un)registration UI for IRegistrable objects
    """
    grok.context(IRegistrable)
    grok.viewletmanager(ISideBar)
    registered = is_member = False
    nick = None
    prompt = None

    def update(self):
        self.nick  = self.request.principal.id
        if (self.request.principal.id != 'admin'
          and self.request.principal.id != 'zope.anybody'):
            self.is_member = True
        if IRegistration(self.context).is_registered(self.nick):
            self.prompt = _(u'You are already registered')
            self.registered = True
        self.addme_label = _(u'I want to attend!')
        self.removeme_label = _(u'I don\'t want to attend')


class Register(grok.View):
    """view that really does the (un)registration
    but is independent from any rendering or template
    """
    grok.context(IRegistrable)
    grok.require('afpy.barcamp.can_attend')
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

        # store the nick in the session
        # TODO should be removed since we use auth
        ISession(self.request)['afpy.barcamp']['nick'] = self.nick
        # Display a message for the next page
        msg = _(u'You have been added to: %s')
        SessionMessageSource().send(translate(msg, context=self.request) % self.context.name)
        self.redirect(self.url(''))

    def unregister(self):
        if IRegistration(self.context).is_registered(self.nick):
            # unregister the person
            IRegistration(self.context).unregister(self.nick)

            # display a message on the next screen
            msg = _(u'You have been removed from: %s')
            SessionMessageSource().send(translate(msg, context=self.request) % self.context.name)
            self.redirect(self.url(''))
