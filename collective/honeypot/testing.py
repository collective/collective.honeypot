# -*- coding: utf-8 -*-

from zope.component import getSiteManager
from Acquisition import aq_base
from Products.MailHost.interfaces import IMailHost
from Products.CMFPlone.tests.utils import MockMailHost
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer


def patch_mailhost(portal):
    portal._updateProperty('email_from_address', 'webmaster@example.org')
    portal._original_MailHost = portal.MailHost
    portal.MailHost = mailhost = MockMailHost('MailHost')
    sm = getSiteManager(context=portal)
    sm.unregisterUtility(provided=IMailHost)
    sm.registerUtility(mailhost, provided=IMailHost)


def unpatch_mailhost(portal):
    portal.MailHost = portal._original_MailHost
    sm = getSiteManager(context=portal)
    sm.unregisterUtility(provided=IMailHost)
    sm.registerUtility(aq_base(portal._original_MailHost),
                       provided=IMailHost)


class BasicFixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.honeypot
        self.loadZCML(package=collective.honeypot)

    def setUpPloneSite(self, portal):
        patch_mailhost(portal)

    def teardownPloneSite(self, portal):
        unpatch_mailhost(portal)


class FixesFixture(PloneSandboxLayer):
    # Fixture that loads fixes.zcml.  This activates the improved
    # templates and scripts.
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.honeypot
        self.loadZCML(package=collective.honeypot)
        self.loadZCML(package=collective.honeypot, name='fixes.zcml')

    def setUpPloneSite(self, portal):
        patch_mailhost(portal)

    def teardownPloneSite(self, portal):
        unpatch_mailhost(portal)


BASIC_FIXTURE = BasicFixture()
FIXES_FIXTURE = FixesFixture()
BASIC_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(BASIC_FIXTURE,),
    name='collective.honeypot:BasicFunctional',
)
FIXES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXES_FIXTURE,),
    name='collective.honeypot:FixesFunctional',
)