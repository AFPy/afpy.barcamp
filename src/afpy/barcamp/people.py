from grokcore import formlib
from md5 import md5
from zope.app.container.browser.contents import Contents
from zope.app.container.interfaces import IContainer
from zope.interface import Interface, implements
from zope.schema import TextLine, Password, Text
from zope.securitypolicy.interfaces import IPrincipalRoleManager
import grok
import megrok.menu
import re
from zope.i18nmessageid import MessageFactory
_ = MessageFactory('afpy.barcamp')

check_email = re.compile(
    r"^[a-zA-Z0-9\._%-]+@([a-zA-Z0-9_-]+\.)*[a-zA-Z]{2,4}$").match


class IPeople(IContainer):
    """interface of a person
    """
    login = TextLine(title=_(u'Login'))
    firstname = TextLine(title=_(u'Firstname'))
    lastname = TextLine(title=_(u'Lastname'))
    email = TextLine(title=_(u'E-mail'),
                     constraint = check_email)
    phone = TextLine(title=_(u'Telephone'), required=False)
    password = Password(title=_(u'Password'))
    shortbio = Text(title=_(u'Short bio'),
                    description=_(u'Short description of yourself'),
                    required=False)


class People(grok.Container):
    """a person (attendee or speaker)
    """
    login = _password = None
    firstname = lastname = None
    email = phone = shortbio = None
    implements(IPeople)

    def _set_password(self, password):
        """store a hash of the password
        """
        self._password = md5(password).digest()

    def _get_password(self):
        """shouldn't be used
        """
        return self._password

    password = property(_get_password, _set_password)

    def check_password(self, password):
        """compare the hashes of the passwords
        return True if the password is ok.
        """
        if self.password == md5(password).digest():
            return True
        return False

class Index(formlib.DisplayForm):
    """the view of the person
    """
    grok.context(People)
    grok.require('zope.ManageContent')
    form_fields = grok.AutoFields(IPeople).omit('password')
    megrok.menu.menuitem('actions')
    grok.title(_(u'View'))


class IPeopleContainer(IContainer):
    pass


class PeopleContainer(grok.Container):
    """the container for people
    """
    implements(IPeopleContainer)


class PeopleListView(Contents, grok.View):
    """view for the list of people
    """
    grok.name('index')
    grok.context(PeopleContainer)
    grok.require('zope.ManageContent')
    megrok.menu.menuitem('navigation')
    grok.title(u'People')


class Add(formlib.AddForm):
    """add form for a person
    """
    grok.context(PeopleContainer)
    form_fields = grok.AutoFields(IPeople)
    grok.require('zope.ManageContent')
    prefix = "people" # to avoid conflit with session credentials
    megrok.menu.menuitem('actions')
    grok.title(u'Add a person')

    @formlib.action('Add this person')
    def add(self, **data):
        obj = People()
        self.applyData(obj, **data)

        # TODO generate a correct slug that removes accents
        login = data['login'].lower().replace(' ', '_')
        self.context[login] = obj

        # grant him the Member role
        # TODO in a IObjectAddedEvent instead
        prm = IPrincipalRoleManager(grok.getSite())
        prm.assignRoleToPrincipal('afpy.barcamp.Member', obj.login)

        self.redirect(self.url('index'))


class Edit(formlib.EditForm):
    """edit form for a person
    """
    form_fields = grok.AutoFields(IPeople)
    grok.context(People)
    grok.require('zope.ManageContent')
    megrok.menu.menuitem('actions')
    grok.title(u'Edit')

