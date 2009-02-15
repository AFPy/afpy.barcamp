from afpy.barcamp.registration import IRegistrable
from afpy.barcamp.interfaces import IRegistration
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
    name = None
    start_date = None
    duration = None
    description = None
    authors = None


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


class SeanceListEdit(Contents, grok.View):
    """view of the list of seances
    """
    grok.name('edit')
    grok.context(SeanceContainer)


class AddSeancePermission(grok.Permission):
    grok.name('afpy.barcamp.addseance')
    grok.title('Add a seance') # optional


class Add(formlib.AddForm):
    """add form for a seance
    """
    grok.require('afpy.barcamp.addseance')
    grok.context(SeanceContainer)
    form_fields = grok.AutoFields(ISeance).omit('start_date')

    def update(self):
        form = self.request.form

        # we automatically register for the meeting (which is the nearest Site)
        IRegistration(grok.getSite()).register(self.request.principal.id)

        if not form.get('form.author', '').strip():
            form['form.author'] = \
                         ISession(self.request)['afpy.barcamp'].get('nick')

        super(Add, self).update()

    @formlib.action('Add seance')
    def add(self, **data):

        obj = Seance()
        self.applyData(obj, **data)

        # TODO generate a correct blurb that removes accents
        name = data['name'].lower().replace(' ', '_')
        self.context[name] = obj
        self.redirect(self.url('index'))



