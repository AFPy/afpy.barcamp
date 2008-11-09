from afpy.barcamp.people import People, IPeopleContainer
from grokcore import formlib
from z3c.flashmessage.sources import SessionMessageSource
from zope.app.container.browser.contents import Contents
from zope.app.container.interfaces import IContainer
from zope.component import getUtility
from zope.interface import implements, Interface, Attribute
from zope.schema import Datetime, TextLine
from zope.security.interfaces import Unauthorized
from zope.session.interfaces import ISession as IZopeSession
import grok

class ISession(IContainer):
    """interface of a session
    """
    name = TextLine(title=u'name')
    date = Datetime(title=u'date', required=False)
    nicknames = Attribute(u'names of persons attending the session')


class Session(grok.Container):
    """the session itself
    """
    implements(ISession)
    name = date = None

    def __init__(self):
        self.nicknames = set()
        super(Session, self).__init__()


class Index(formlib.DisplayForm):
    """view of the session
    """
    form_fields = grok.AutoFields(ISession)
    grok.context(Session)


class Edit(formlib.EditForm):
    """edit form for the session
    """
    form_fields = grok.AutoFields(ISession)
    grok.context(Session)


class ISessionContainer(IContainer):
    pass

class SessionContainer(grok.Container):
    """the container for sessions
    """


class SessionListView(Contents, grok.View):
    """view of the list of sessions
    """
    grok.name('index')
    grok.context(SessionContainer)


class Add(formlib.AddForm):
    """add form for a session
    """
    grok.context(SessionContainer)
    form_fields = grok.AutoFields(ISession)

    def setUpWidgets(self, ignore_request = False):
        super(Add, self).setUpWidgets(ignore_request)

    @formlib.action('Add session')
    def add(self, **data):
        obj = Session()
        self.applyData(obj, **data)
        # TODO generate a correct blurb that removes accents
        name = data['name'].lower().replace(' ', '_')
        self.context[name] = obj
        self.redirect(self.url('index'))

class RegistrationPage(grok.View):
    """view to register to a session
    """
    grok.context(Session)
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

        self.postednick = self.request.get('nickname')
        if self.postednick:
            self.register(self.postednick)
            msg = (u'You have been added to'
                   u' the %s event!'
                    % self.context.__name__)
            SessionMessageSource().send(msg)
            self.redirect(self.url(''))

    def register(self, nick):
        peoplelist = getUtility(IPeopleContainer)
        if nick in peoplelist:
            people = peoplelist[nick]
            if people.is_private():
                raise Unauthorized('barre oit')
        else:
            people = People()
            people.name = nick
            peoplelist[nick] = people
            IZopeSession(self.request)['afpy.barcamp']['nick'] = nick
        self.context.nicknames.add(nick)

class Unregister(grok.View):
    grok.context(Session)

    def update(self):
        nick = IZopeSession(self.request)['afpy.barcamp'].get('nick')
        if nick in self.context.nicknames:
            self.context.nicknames.remove(nick)
            msg = (u'You have been removed from'
                   u' the %s event!'
                    % self.context.__name__)
            SessionMessageSource().send(msg)
            self.redirect(self.url(''))

    def render(self):
        pass


class Registration(grok.View):
    grok.context(Session)

    def update(self):
        self.nick = IZopeSession(self.request)['afpy.barcamp'].get('nick')



