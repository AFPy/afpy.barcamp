from afpy.barcamp.registration import IRegistrable
from zope.interface import implements
from grokcore import formlib
from zope.app.container.browser.contents import Contents
from interfaces import ISession, ISessionContainer
from zope.session.interfaces import ISession as IZopeSession
import grok

class Session(grok.Container):
    """the session itself
    """
    implements(ISession, IRegistrable)
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

    def update(self):
        form = self.request.form

        if not form.get('form.author', '').strip():
            form['form.author'] = IZopeSession(
                    self.request)['afpy.barcamp'].get('nick')

        super(Add, self).update()
        
    @formlib.action('Add session')
    def add(self, **data):

        obj = Session()
        self.applyData(obj, **data)

        # TODO generate a correct blurb that removes accents
        name = data['name'].lower().replace(' ', '_')
        self.context[name] = obj
        self.redirect(self.url('index'))



