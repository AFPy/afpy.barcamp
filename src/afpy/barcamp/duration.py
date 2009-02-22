from grokcore import formlib
from zc.sourcefactory.basic import BasicSourceFactory
from zope.app.container.browser.contents import Contents
from zope.app.container.interfaces import IContainer
from zope.component import getUtility
from zope.interface import Interface, Attribute
from zope.interface import implements
from zope.schema import Datetime, TextLine, Text, Int, Choice
import grok
import megrok.menu
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('afpy.barcamp')

class IDurations(IContainer):
    """interface of the container of durations
    """


class IDuration(Interface):
    """interface of a duration
    """
    value = Int(title=_(u'Duration in minutes'))
    title = TextLine(title=_(u'Title'))


class Durations(grok.Container):
    """a container for configurable seance durations
    """
    implements(IDurations)

    def __init__(self):
        super(Durations, self).__init__()
        # prefill the durations with default values
        if len(self) == 0:
            self['lightning'] = Duration(10, u'Lightning Talk (10min)')
            self['presentation'] = Duration(20, u'Presentation (20min)')
            self['tutoriel'] = Duration(60, u'Tutoriel (1h)')
            self['atelier'] = Duration(120, u'Atelier (2h)')
    

class Duration(grok.Model):
    """a duration
    """
    implements(IDuration)

    def __init__(self, value=None, title=None):
        super(Duration, self).__init__()
        self.value = value
        self.title = title


class Add(formlib.AddForm):
    """add form for a duration
    """
    grok.context(Durations)
    form_fields = grok.AutoFields(IDuration)
    grok.require('zope.ManageContent')
    megrok.menu.menuitem('actions')
    grok.title(_(u'Add a duration'))

    @formlib.action('Add')
    def add(self, **data):
        obj = Duration()
        self.applyData(obj, **data)

        name = data['title'].lower().replace(' ', '_')
        self.context[name] = obj
        self.redirect(self.url('index'))


class Index(formlib.DisplayForm):
    """view of the durations
    """
    form_fields = grok.AutoFields(IDuration)
    grok.require('zope.ManageContent')
    grok.context(IDuration)
    megrok.menu.menuitem('actions')
    grok.title(_(u'View'))


class Edit(formlib.EditForm):
    """edit form for a duration
    """
    form_fields = grok.AutoFields(IDuration)
    grok.context(Duration)
    grok.require('zope.ManageContent')
    megrok.menu.menuitem('actions')
    grok.title(_(u'Edit'))

class DurationSource(BasicSourceFactory):
    """source for the durations
    It allows to associate a title to a value
    for each duration, in the dropdown list
    """
    def getValues(self):
        values = list(getUtility(IDurations).values())
        values.sort(key=lambda x: getattr(x,'value'))
        return values

    def getTitle(self, value):
        return value.title


class ListView(Contents, grok.View):
    """view of the list of durations
    """
    grok.name('index')
    grok.context(IDurations)
    grok.require('zope.ManageContent')
    megrok.menu.menuitem('navigation')
    grok.title(_(u'Durations'))


