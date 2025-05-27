# -*- coding: utf-8 -*-
from Acquisition import aq_base
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.base.utils import get_installer
from plone.registry.interfaces import IRegistry
from plone.testing import zope
from plone.testing import z2
from Products.CMFPlone.tests.utils import MockMailHost
from Products.MailHost.interfaces import IMailHost
from zope.component import getSiteManager
from zope.component import queryUtility

import collective.honeypot.config
import plone.restapi

# We want ALLOWLISTED_START to be empty by default currently, but we
# do want to test it.
start = list(collective.honeypot.config.ALLOWLISTED_START)
start.append("jq_")
collective.honeypot.config.ALLOWLISTED_START = set(start)


def patch_mailhost(portal):
    registry = queryUtility(IRegistry)
    registry["plone.email_from_address"] = "webmaster@example.org"
    portal._original_MailHost = portal.MailHost
    portal.MailHost = mailhost = MockMailHost("MailHost")
    mailhost.smtp_host = "localhost"
    sm = getSiteManager(context=portal)
    sm.unregisterUtility(provided=IMailHost)
    sm.registerUtility(mailhost, provided=IMailHost)


def unpatch_mailhost(portal):
    portal.MailHost = portal._original_MailHost
    sm = getSiteManager(context=portal)
    sm.unregisterUtility(provided=IMailHost)
    sm.registerUtility(aq_base(portal._original_MailHost), provided=IMailHost)


class HoneypotFixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.honeypot
        import plone.app.discussion

        self.loadZCML(package=collective.honeypot)
        self.loadZCML(package=plone.app.discussion)

    def setUpPloneSite(self, portal):
        patch_mailhost(portal)
        # Enable commenting, self registration, and sending mail.
        installer = get_installer(portal)
        installer.install_product("plone.app.discussion")
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        settings.globally_enabled = True
        settings.anonymous_comments = True
        portal.manage_permission("Reply to item", ("Anonymous", "Manager"))
        portal.manage_permission("Allow sendto", ("Anonymous", "Manager"))
        portal.manage_permission("Add portal member", ("Anonymous", "Manager"))

    def teardownPloneSite(self, portal):
        unpatch_mailhost(portal)


HONEYPOT_FIXTURE = HoneypotFixture()
HONEYPOT_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(HONEYPOT_FIXTURE,),
    name="collective.honeypot:Functional",
)


class HoneypotRestApiFixture(HoneypotFixture):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        super(HoneypotRestApiFixture, self).setUpZope(app, configurationContext)
        self.loadZCML(package=plone.restapi)


HONEYPOT_API_FIXTURE = HoneypotRestApiFixture()

HONEYPOT_API_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(HONEYPOT_API_FIXTURE, z2.ZSERVER_FIXTURE),
    name="HoneypotRestApiFixture:Functional",
)
