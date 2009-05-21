from afpy.barcamp.interfaces import IRegistration
from afpy.barcamp.people import IPeopleContainer
from afpy.barcamp.registration import IRegistrable
from datetime import date, timedelta
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
import xlwt
import os
import tempfile
import itertools
import logging

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

class ExportView(Contents, grok.View):
    """view of the list of seances
    """
    grok.name('export')
    grok.context(SeanceContainer)
    grok.require('afpy.barcamp.seances.list')
    grok.title(_(u'export'))

    def render(self):
        datefmt = self.request.locale.dates.getFormatter('date').format
        site = grok.getSite()
        durations = [dur.title for dur in site['durations'].values()]

        # Excel styling
        base_sty_str = 'border: top thin, left thin, right thin, bottom thin; align: wrap yes, vert centre, horz centre;'
        colors = itertools.cycle(('coral',
                                  'light_green',
                                  'tan',
                                  'ivory',
                                  'pale_blue',
                                  'light_yellow',
                                  'lavender',
                                  'grey25',
                                  'rose',
                                  'light_turquoise',
                                  'periwinkle',
                                  'ice_blue',)) # Just in case we have more than 12 different durations
        header_sty = xlwt.easyxf(base_sty_str+'font: bold on')
        durations = dict((d, xlwt.easyxf(base_sty_str+'pattern: pattern solid, fore-colour %s;' % colors.next())) for d in durations)

        wb = xlwt.Workbook()

        seances = [v for v in self.context.values()
                   if v.status == 'confirmed' and v.start_date is not None]
        rooms = sorted(set(s.room.title for s in seances))

        by_date = dict()
        errors = []
        for s in seances:
            by_date.setdefault(s.start_date.timetuple()[:3], []).append(s)
        for date_tuple, day_seances in sorted(by_date.iteritems()):
            sheet_name = datefmt(date(*date_tuple))
            by_room = dict()
            for s in day_seances:
                by_room.setdefault(s.room.title, []).append(s)
            ws = wb.add_sheet(sheet_name)
            start_hour = min(s.start_date.hour for s in day_seances)
            end_hour = max(s.end_date.hour for s in day_seances)+1
            hours = ['%d:%.2d' % (k, v) for k in xrange(start_hour, end_hour) for v in xrange(0, 60, 15)]
            for line, h in enumerate(hours):
                ws.write(line+1, 0, h, header_sty)
            for col, room in enumerate(rooms):
                ws.col(col+1).width = 0x2500
                ws.write(0, col+1, room, header_sty)
                for seance in by_room.get(room, []):
                    start_line = 1+(seance.start_date.hour-start_hour)*4+seance.start_date.minute/15
                    minutes_step, mod = divmod(seance.duration.value, 15)
                    if mod == 0:
                        minutes_step -= 1
                    end_line = start_line + minutes_step
                    try:
                        ws.write_merge(start_line, end_line, col+1, col+1, seance.name, durations[seance.duration.title])
                    except:
                        errors.append(seance)

            # write legend
            start = len(hours)+3
            for i, (value, style) in enumerate(sorted(durations.iteritems())):
                ws.write(start+i, 1, value, style)

            ws.show_grid = False
            ws.panes_frozen = True
            ws.horz_split_pos = 1
            ws.vert_split_pos = 1
            ws.portrait = True

        for error in errors:
            logging.error('Seance %s starting on %s and ending on %s in room %s is overriding another seance',
                          error.name,
                          error.start_date,
                          error.end_date,
                          error.room.title)

        # output
        fd, fname = tempfile.mkstemp()
        wb.save(fname)
        content = file(fname).read()
        os.close(fd)
        os.unlink(fname)
        self.request.response.setHeader('Content-type', 'application/vnd.ms-excel')
        self.request.response.setHeader('Content-disposition', 'attachment; filename=planning.xls')
        return content

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
