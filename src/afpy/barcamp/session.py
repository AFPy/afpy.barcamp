from grokcore import formlib
from zope.app.container.browser.contents import Contents
from zope.app.container.interfaces import IContainer
from zope.interface import implements, Interface
from zope.schema import Datetime, TextLine
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

