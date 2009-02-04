"""This module defines all the needed elements to handle registration.
The registration concept we have developped is working for any kind of resources
Sessions and Meetings, the only condition is to implement IRegistrable. Once your
resource implements IRegistrable it can use our registration component to
provide the user/visitor registration.

In our application it is important to understand that a visitor is not always
logged-in and that we do not want to force all visitors to log-in. This is why
we try to just use the session cookie of our visitors, to keep track of their
nicknames (the thing we call nick in our code).

Anyone is authorized to _claim_ a nickname as their own. In this case the people
object associated with that nickname will be marked as private. If someone
tries to use a nickname that is associated with a private people object then we
will ask her for the good credentials.
"""

# our own application imports
from afpy.barcamp.interfaces import ISideBar
from afpy.barcamp.people import People, IPeopleContainer
from afpy.barcamp.interfaces import IRegistrable

# zope & co
from z3c.flashmessage.sources import SessionMessageSource
from zope.component import getUtility
from zope.interface import Interface
from zope.security.interfaces import Unauthorized
from zope.session.interfaces import ISession as IZopeSession

# grok
import grok


class RegistrationPage(grok.View):
    """Page to register to a session or meeting, and used for the UI.
    """
    grok.context(IRegistrable)
    registered = False
    nick = None

    def update(self):
        # default prompt if we don't find an active nickname in the web-session
        self.prompt = u'Please enter your nickname'

        if 'new' not in self.request:
            # new is not in the request, which means the user already has a
            # nick associated to his web-session. Let's fetch that...
            self.nick = IZopeSession(self.request)['afpy.barcamp'].get('nick')

        if self.nick:
            # if we found a nickname in the web-session we compare with
            # the registered users to see if the nick is present and warn
            # the user if so...
            if self.nick in self.context.nicknames:
                self.prompt = u'You are already registered'
                self.registered = True

            else:
                # we found a nickname and the user is not yet registered to this
                # registerable element, we just ask for the nick confirmation.
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
                raise Unauthorized('This profile is private. Please Log-In.')

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
