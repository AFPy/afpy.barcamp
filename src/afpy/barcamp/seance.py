from afpy.barcamp.interfaces import IRegistration
from zope.component import getUtility
from afpy.barcamp.people import IPeopleContainer
from afpy.barcamp.registration import IRegistrable
from grokcore import formlib
from interfaces import ISeance, ISeanceContainer
from z3c.flashmessage.sources import SessionMessageSource
from zope.app.container.browser.contents import Contents
from zope.interface import implements
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from zope.session.interfaces import ISession
import megrok.menu
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
    status = 'proposed'

    def __init__(self):
        super(Seance, self).__init__()
        if self.authors is None:
            self.authors = set()


class Index(formlib.DisplayForm):
    """view of the seance
    """
    form_fields = grok.AutoFields(ISeance).omit('name')
    grok.context(ISeance)
    megrok.menu.menuitem('actions')
    grok.title(u'View')


class EditPermission(grok.Permission):
    grok.name('afpy.barcamp.editseance')
    grok.title('Edit a seance') # optional


class Edit(formlib.EditForm):
    """edit form for the seance
    """
    form_fields = grok.AutoFields(ISeance)
    grok.require('afpy.barcamp.editseance')
    grok.context(ISeance)
    grok.title(u'Edit')
    megrok.menu.menuitem('actions')


class SeanceContainer(grok.Container):
    """the container for seances
    """


class ListPermission(grok.Permission):
    """can only see some pages when authenticated
    ex: the list of proposed seances
    """
    grok.name('afpy.barcamp.seances.list')
    grok.title('View the list of seances') # optional


class ListView(Contents, grok.View):
    """view of the list of seances
    """
    grok.name('index')
    grok.context(SeanceContainer)
    grok.require('afpy.barcamp.seances.list')
    megrok.menu.menuitem('navigation')
    grok.title(u'Proposed seances')


class ListEdit(Contents, grok.View):
    """view of the list of seances
    """
    grok.name('edit')
    grok.context(SeanceContainer)
    grok.require('zope.ManageContent')


class AddPermission(grok.Permission):
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

        # add the author
        obj.authors.add(self.request.principal.id)

        # TODO generate a correct slug that removes accents
        name = data['name'].lower().replace(' ', '_')
        self.context[name] = obj
        # assign a local role, just for this seance
        IPrincipalRoleManager(obj
                         ).assignRoleToPrincipal('afpy.barcamp.SeanceLeader',
                                                 self.request.principal.id)

        self.redirect(self.url(obj)+ '/@@added')


class Added(grok.View):
    """Confirmation page after a seance is proposed
    """
    grok.name('added')
    grok.context(ISeance)

class SeanceLeaderRole(grok.Role):
    """role assigned to speakers on their own seances
    """
    grok.name('afpy.barcamp.SeanceLeader')
    grok.title('Leader of a seance') # optional
    grok.permissions(
        'afpy.barcamp.editseance')



