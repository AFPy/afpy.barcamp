from afpy.barcamp.people import People, IPeopleContainer
from grokcore import formlib
from z3c.flashmessage.sources import SessionMessageSource
from zope.app.container.browser.contents import Contents
from zope.app.container.interfaces import IContainer
from zope.component import getUtility
from zope.interface import implements, Interface
from zope.schema import Datetime, TextLine
from zope.security.interfaces import Unauthorized
from zope.session.interfaces import ISession as IZopeSession
import grok

class ISession(IContainer):
    """interface of a session
    """
    name = TextLine(title=u'name')
    date = Datetime(title=u'date')


class Session(grok.Container):
    """the session itself
    """
    implements(ISession)
    name = date = None


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

class Register(grok.View):
    """view to register to a session
    """
    grok.context(Session)

    def update(self):
        self.prompt = u'Please enter your nickname'
        self.sessionnick = IZopeSession(self.request)['afpy.barcamp'].get('nick')
        if self.sessionnick:
            self.prompt = u'Please confirm your nickname'

        self.postednick = self.request.get('nickname')
        if self.postednick:
            self.register(self.postednick)
            msg = (u'You have successfully registered'
                   u' to the %s event!'
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


