from grokcore import formlib
from zope.app.container.browser.contents import Contents
from zope.app.container.interfaces import IContainer
from zope.interface import Interface, implements
from zope.schema import TextLine
import grok

class IPeople(IContainer):
    """interface of a people"""
    
    name = TextLine(title=u'name')


class People(grok.Container):
    """the person that is supposed to make a presentationi
    """
    name = None
    implements(IPeople)


class Index(formlib.DisplayForm):
    """the view of the person
    """
    grok.context(People)


class PeopleContainer(grok.Container):
    """the cotainer for people
    """

class PeopleListView(Contents, grok.View):
    """view for the list of people
    """
    grok.name('index')
    grok.context(PeopleContainer)


class Add(formlib.AddForm):
    """add form for a person
    """
    grok.context(PeopleContainer)
    form_fields = grok.AutoFields(IPeople)

    def setUpWidgets(self, ignore_request = False):
        super(Add, self).setUpWidgets(ignore_request)

    @formlib.action('Add this person')
    def add(self, **data):
        obj = People()
        self.applyData(obj, **data)
        # TODO generate a correct blurb that removes accents
        name = data['name'].lower().replace(' ', '_')
        self.context[name] = obj
        self.redirect(self.url('index'))


class Edit(formlib.EditForm):
    """edit form for a person
    """
    form_fields = grok.AutoFields(IPeople)
    grok.context(People)
