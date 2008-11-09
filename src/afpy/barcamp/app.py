import grok
from afpy.barcamp.interfaces import ISideBar
from afpy.barcamp.event import IEvent, Event
from zope.interface import implements
from zope.app.container.browser.contents import Contents
from zope.interface import Interface
from grokcore import formlib

class AfpyBarcamp(grok.Application, grok.Container):
    pass


class Index(Contents, grok.View):
    pass # see app_templates/index.pt


class AddEvent(formlib.AddForm):
    grok.context(AfpyBarcamp)
    form_fields = grok.AutoFields(IEvent)

    def setUpWidgets(self, ignore_request = False):
        super(AddEvent, self).setUpWidgets(ignore_request)

    @formlib.action('Add event')
    def add(self, **data):
        obj = Event()
        self.applyData(obj, **data)
        # TODO generate a correct blurb that removes accents
        name = data['name'].lower().replace(' ', '_')
        self.context[name] = obj
        self.redirect(self.url('index'))


class BarcampToplevelMacros(grok.View):
    """The view providing the global macros for view upper than event level
    """
    grok.context(Interface)


class BarcampMacros(grok.View):
    """The view providing the global macros for event under the event level
    """
    grok.context(Interface)


class SideBar(grok.ViewletManager):
    """a viewlet manager used to hold some viewlets.
    It can be used as a sidebar
    """
    implements(ISideBar)
    grok.name('sidebar')
    grok.view(Interface)
    grok.context(Interface)



