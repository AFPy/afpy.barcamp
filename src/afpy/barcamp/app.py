import grok
from afpy.barcamp.event import IEvent, Event

class AfpyBarcamp(grok.Application, grok.Container):
    pass

class Index(grok.View):
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
