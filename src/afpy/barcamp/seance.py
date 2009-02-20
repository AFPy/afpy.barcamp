from afpy.barcamp.interfaces import IRegistration
from zope.component import getUtility
from afpy.barcamp.people import IPeopleContainer
from afpy.barcamp.registration import IRegistrable
from grokcore import formlib
from interfaces import ISeance, ISeanceContainer
from z3c.flashmessage.sources import SessionMessageSource
from zope.app.container.browser.contents import Contents
from zope.interface import implements
from zope.securitypolicy.interfaces import IPrincipalPermissionManager
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
    status = None


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
    grok.require('zope.ManageContent')


class AddSeancePermission(grok.Permission):
    grok.name('afpy.barcamp.addseance')
    grok.title('Add a seance') # optional


class Add(formlib.AddForm):
    """add form for a seance
    """
    grok.require('afpy.barcamp.addseance')
    grok.context(SeanceContainer)
    form_fields = grok.AutoFields(ISeance).omit('start_date', 'status')

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
        nick = self.request.principal.id
        peoplelist = getUtility(IPeopleContainer, context=grok.getSite())

        if nick not in peoplelist:
            msg = (u'Please first register')
            SessionMessageSource().send(msg)
            self.redirect(self.url(''))

        obj = Seance()
        self.applyData(obj, **data)

        # TODO generate a correct blurb that removes accents
        name = data['name'].lower().replace(' ', '_')
        self.context[name] = obj
        IPrincipalPermissionManager(obj)\
            .grantPermissionToPrincipal('zope.ManageContent',
                                        self.request.principal.id)
        self.redirect(self.url('index'))



