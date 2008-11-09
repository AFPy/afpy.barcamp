from afpy.barcamp.app import ISideBar
from afpy.barcamp.people import People, IPeopleContainer
from z3c.flashmessage.sources import SessionMessageSource
from zope.component import getUtility
from zope.interface import Interface
from zope.security.interfaces import Unauthorized
from interfaces import IRegistrable
from zope.session.interfaces import ISession as IZopeSession
import grok


class RegistrationPage(grok.View):
    """Page to register to a session or event, and used for the UI.
    """
    grok.context(IRegistrable)
    registered = False
    nick = None

    def update(self):
        self.prompt = u'Please enter your nickname'
        if 'new' not in self.request:
            self.nick = IZopeSession(self.request)['afpy.barcamp'].get('nick')
        if self.nick:
            if self.nick in self.context.nicknames:
                self.prompt = u'You are already in this session'
                self.registered = True
            else:
                self.prompt = u'Please confirm your nickname'


class RegistrationViewlet(grok.Viewlet):
    """viewlet that offers (un)registration UI for IRegistrable objects
    """
    grok.context(IRegistrable)
    grok.viewletmanager(ISideBar)
    registered = loggedin = False
    nick = None

    def update(self):
        self.nick = IZopeSession(self.request)['afpy.barcamp'].get('nick')
        if self.nick:
            self.loggedin = True
        if self.nick in self.context.nicknames:
            self.registered = True


class Registration(grok.View):
    """view that really does the (un)registration
    but is independent from any rendering or template
    """
    grok.context(IRegistrable)
    grok.traversable('register') # allows to access @@registration/register
    grok.traversable('unregister')

    def update(self):
        if 'unregister' in self.request:
            self.unregister()
        if 'register' in self.request:
            self.register()

    def render(self):
        pass

    def register(self):
        nick = IZopeSession(self.request)['afpy.barcamp'].get('nick')
        # get the nick given in the form
        postednick = self.request.get('nickname')
        if postednick:
            nick = postednick
        # retrieve or create the associated people
        peoplelist = getUtility(IPeopleContainer)
        if nick in peoplelist:
            people = peoplelist[nick]
            if people.is_private():
                raise Unauthorized('barre oit')
        else:
            people = People()
            people.name = nick
            peoplelist[nick] = people
        # do the registration
        self.context.nicknames.add(nick)
        IZopeSession(self.request)['afpy.barcamp']['nick'] = nick
        msg = (u'You have been added to %s!' % self.context.name)
        SessionMessageSource().send(msg)
        self.redirect(self.url(''))

    def unregister(self):
        nick = IZopeSession(self.request)['afpy.barcamp'].get('nick')
        if nick in self.context.nicknames:
            self.context.nicknames.remove(nick)
            msg = (u'You have been removed from %s!' 
                   % self.context.name)
            SessionMessageSource().send(msg)
            self.redirect(self.url(''))


