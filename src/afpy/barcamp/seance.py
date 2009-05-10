from afpy.barcamp.interfaces import IRegistration
from afpy.barcamp.people import IPeopleContainer
from afpy.barcamp.registration import IRegistrable
from datetime import timedelta
from grokcore import formlib
from interfaces import ISeance
from z3c.flashmessage.sources import SessionMessageSource
from zope.app.container.browser.contents import Contents
from zope.app.form.browser.textwidgets import escape
from zope.app.renderer.plaintext import PlainTextToHTMLRenderer
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory
from zope.interface import implements
from zope.securitypolicy.interfaces import IPrincipalRoleManager
from zope.session.interfaces import ISession
import grok
import megrok.menu
_ = MessageFactory('afpy.barcamp')

class Seance(grok.Container):
    """the seance itself
    """
    implements(ISeance, IRegistrable)
    name = audience = description = None
    start_date = duration = benefits = None
    room = None
    keywords = authors = unfolding = None
    status = 'proposed'

    def __init__(self):
        super(Seance, self).__init__()
        if self.authors is None:
            self.authors = set()

    @property
    def end_date(self):
        if type(self.duration.value) == int:
            return (self.start_date
                    + timedelta(minutes=self.duration.value))
        return self.start_date


class Index(formlib.DisplayForm):
    """view of the seance
    """
    form_fields = grok.AutoFields(ISeance).omit('name')
    #grok.require('afpy.barcamp.seances.list')
    grok.context(ISeance)
    megrok.menu.menuitem('actions')
    grok.title(_(u'View'))


class EditPermission(grok.Permission):
    grok.name('afpy.barcamp.editseance')
    grok.title(_(u'Edit a seance')) # optional


class Edit(formlib.EditForm):
    """edit form for the seance
    """
    form_fields = grok.AutoFields(ISeance)
    grok.require('afpy.barcamp.editseance')
    grok.context(ISeance)
    grok.title(_(u'Edit'))
    megrok.menu.menuitem('actions')


class SeanceContainer(grok.Container):
    """the container for seances
    """


class ListPermission(grok.Permission):
    """can only see some pages when authenticated
    ex: the list of proposed seances
    """
    grok.name('afpy.barcamp.seances.list')
    grok.title(_(u'View the list of seances')) # optional


def start_date_sort(a, b):
    if a.start_date is None:
        return 1
    if b.start_date is None:
        return -1
    return cmp(a.start_date, b.start_date)


class ListView(Contents, grok.View):
    """view of the list of seances
    """
    grok.name('index')
    grok.context(SeanceContainer)
    grok.require('afpy.barcamp.seances.list')
    megrok.menu.menuitem('navigation')
    grok.title(_(u'Proposed seances'))

    def update(self):
        self.sorted_seances = list(self.context.values())
        self.sorted_seances.sort(start_date_sort)
        super(ListView, self).update()


class ListEdit(Contents, grok.View):
    """edit the list of seances
    """
    grok.name('edit')
    grok.context(SeanceContainer)
    grok.require('zope.ManageContent')
    megrok.menu.menuitem('actions')
    grok.title(_(u'Edit'))


class AddPermission(grok.Permission):
    grok.name('afpy.barcamp.addseance')
    grok.title(_(u'Add a seance')) # optional


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

    @formlib.action(_(u'Add seance'))
    def add(self, **data):
        nick = self.request.principal.id
        peoplelist = getUtility(IPeopleContainer, context=grok.getSite())

        if nick not in peoplelist:
            msg = _(u'Please first register')
            SessionMessageSource().send(msg)
            self.redirect(self.url(''))

        obj = Seance()
        self.applyData(obj, **data)

        # add the author
        obj.authors.add(self.request.principal.id)

        # TODO generate a correct slug that removes accents
        name = data['name'].lower().replace(' ', '_').replace('/','_')
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
    grok.title(_(u'Leader of a seance')) # optional
    grok.permissions(
        'afpy.barcamp.editseance')


class HtmlDescription(grok.View):
    """an html view for the descriptions
    """
    grok.name('htmldescription')
    grok.title('html')
    grok.context(ISeance)

    def render(self):
        if self.context.description is None:
            return _(u'(no description)')
        return PlainTextToHTMLRenderer(escape(
                    self.context.description),
                    self.request).render()

