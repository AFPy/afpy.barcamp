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


class Index(grok.DisplayForm):
    """view of the event
    """
    form_fields = grok.AutoFields(ISession)


class Edit(grok.EditForm):
    """edit form for the session
    """
    form_fields = grok.AutoFields(ISession)
    grok.context(Session)


class Sessions(grok.Container):
    """the container for sessions
    """


class Index(Contents, grok.View):
    """view of the list of sessions
    """
    grok.context(Sessions)
    grok.template('sessionlist.pt')



