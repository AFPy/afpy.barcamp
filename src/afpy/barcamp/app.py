import grok
from afpy.barcamp.event import IEvent, Event
from zope.app.container.browser.contents import Contents
from zope.interface import Interface

class AfpyBarcamp(grok.Application, grok.Container):
    pass

class Index(Contents, grok.View):
    pass # see app_templates/index.pt


class AddEvent(grok.Form):
    form_fields = grok.AutoFields(IEvent)

    def setUpWidgets(self, ignore_request = False):
        super(AddEvent, self).setUpWidgets(ignore_request)

    @grok.action('Add event')
    def add(self, **data):
        obj = Event(**data)
        # TODO generate a correct blurb that removes accents
        name = data['name'].lower().replace(' ', '_')
        self.context[name] = obj
        self.redirect(self.url('index'))

class BarcampMacros(grok.View):
    """The view providing the global macros"""
    grok.context(Interface)
