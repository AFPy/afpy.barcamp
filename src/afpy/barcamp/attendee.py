import grok

class Attendee(grok.Container):
    """the person that is supposed to make a presentation"""

class Index(grok.View):
    """the view of the person"""

    def render(self): pass
