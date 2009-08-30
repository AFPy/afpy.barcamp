from grokcore import formlib
from zc.sourcefactory.basic import BasicSourceFactory
from zope.app.container.browser.contents import Contents
from zope.app.container.interfaces import IContainer
from zope.component import getUtility
from zope.interface import Interface
from zope.interface import implements
from zope.schema import TextLine, Int
import grok
import megrok.menu
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('afpy.barcamp')

class IRooms(IContainer):
    """interface of the container of rooms
    """


class IRoom(Interface):
    """interface of a room
    """
    title = TextLine(title=_(u'Title'))
    stream_url = TextLine(title=_(u'Video stream URL'),
                          required=False)


class Rooms(grok.Container):
    """a container for configurable rooms
    """
    implements(IRooms)


class Room(grok.Model):
    """a room
    """
    implements(IRoom)
    stream_url = ''

    def __init__(self, title=None):
        super(Room, self).__init__()
        self.title = title


class Add(formlib.AddForm):
    """add form for a room
    """
    grok.context(Rooms)
    form_fields = grok.AutoFields(IRoom)
    grok.require('zope.ManageContent')
    megrok.menu.menuitem('actions')
    grok.title(_(u'Add a room'))

    @formlib.action('Add')
    def add(self, **data):
        obj = Room()
        self.applyData(obj, **data)

        name = data['title'].lower().replace(' ', '_')
        self.context[name] = obj
        self.redirect(self.url('index'))


class Index(formlib.DisplayForm):
    """view of the rooms
    """
    form_fields = grok.AutoFields(IRoom)
    grok.require('zope.ManageContent')
    grok.context(IRoom)
    megrok.menu.menuitem('actions')
    grok.title(_(u'View'))


class Edit(formlib.EditForm):
    """edit form for a room
    """
    form_fields = grok.AutoFields(IRoom)
    grok.context(Room)
    grok.require('zope.ManageContent')
    megrok.menu.menuitem('actions')
    grok.title(_(u'Edit'))

class RoomSource(BasicSourceFactory):
    """source for the rooms
    It allows to associate a title to a value
    for each room, in the dropdown list
    """
    def getValues(self):
        values = list(getUtility(IRooms).values())
        values.sort(key=lambda x: getattr(x,'title'))
        return values

    def getTitle(self, value):
        return value.title


class ListView(Contents, grok.View):
    """view of the list of rooms
    """
    grok.name('index')
    grok.context(IRooms)
    grok.require('zope.ManageContent')
    megrok.menu.menuitem('navigation')
    grok.title(_(u'Rooms'))


