from afpy.barcamp.registration import IRegistrable
from zope.interface import implements
from grokcore import formlib
from zope.app.container.browser.contents import Contents
from interfaces import ISeance, ISeanceContainer
from zope.session.interfaces import ISession
import grok

class Seance(grok.Container):
    """the seance itself
    """
    implements(ISeance, IRegistrable)
    name = date = None

    def __init__(self):
        self.nicknames = set()
        super(Seance, self).__init__()


class Index(formlib.DisplayForm):
    """view of the seance
    """
    form_fields = grok.AutoFields(ISeance)
    grok.context(Seance)


class Edit(formlib.EditForm):
    """edit form for the seance
    """
    form_fields = grok.AutoFields(ISeance)

    grok.context(Seance)


class SeanceContainer(grok.Container):
    """the container for seances
    """


class SeanceListView(Contents, grok.View):
    """view of the list of seances
    """
    grok.name('index')
    grok.context(SeanceContainer)


class Add(formlib.AddForm):
    """add form for a seance
    """
    grok.context(SeanceContainer)
    form_fields = grok.AutoFields(ISeance)

    def update(self):
        form = self.request.form

        if not form.get('form.author', '').strip():
            form['form.author'] = ISession(
                    self.request)['afpy.barcamp'].get('nick')

        super(Add, self).update()

    @formlib.action('Add seance')
    def add(self, **data):

        obj = Seance()
        self.applyData(obj, **data)

        # TODO generate a correct blurb that removes accents
        name = data['name'].lower().replace(' ', '_')
        self.context[name] = obj
        self.redirect(self.url('index'))



