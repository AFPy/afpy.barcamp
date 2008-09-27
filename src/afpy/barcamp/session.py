import grok

class Session(grok.Container):
    """the presentation"""

class Index(grok.View):
    """the view of te presentation"""

    def render(self): pass
