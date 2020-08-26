# -*- coding: utf-8 -*-

from Acquisition import aq_base
from persistent.list import PersistentList
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.registry.interfaces import IRegistry
from plone.testing import z2
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.tests.utils import MockMailHost
from Products.MailHost.interfaces import IMailHost
from zope.component import getSiteManager
from zope.component import queryUtility

import collective.honeypot.config
import pkg_resources


# We want WHITELISTED_START to be empty by default currently, but we
# do want to test it.
start = list(collective.honeypot.config.WHITELISTED_START)
start.append("jq_")
collective.honeypot.config.WHITELISTED_START = set(start)


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


def enable_self_registration(portal):
    # Taken from plone.app.controlpanel
    app_perms = portal.rolesOfPermission(permission="Add portal member")
    reg_roles = []
    for appperm in app_perms:
        if appperm["selected"] == "SELECTED":
            reg_roles.append(appperm["name"])
    if "Anonymous" not in reg_roles:
        reg_roles.append("Anonymous")
    portal.manage_permission("Add portal member", roles=reg_roles, acquire=0)


class BasicFixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.honeypot

        self.loadZCML(package=collective.honeypot)
        # Install product and call its initialize() function
        z2.installProduct(app, "collective.honeypot")

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, "collective.honeypot")

    def tearDown(self):
        # There is some other code that removes profiles from
        # Products.GenericSetup.zcml._profile_registry but not from
        # _profile_regs, maybe because it gets called multiple times,
        # and this results in a KeyError on teardown.  This only
        # happens in Plone 3.3.  I tried fixing it by removing them,
        # but this failed, so as a last resort we ignore the standard
        # tearDown completely in that case.
        super(BasicFixture, self).tearDown()
        import Products.GenericSetup.zcml

    def setUpPloneSite(self, portal):
        patch_mailhost(portal)
        enable_self_registration(portal)
        # Enable commenting.
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        settings.globally_enabled = True
        settings.anonymous_comments = True
        portal.manage_permission("Reply to item", ("Anonymous",))

        # Allow anonymous to the sendto form.  This is disallowed in
        # Plone 4.3.3.
        try:
            from Products.CMFPlone.PloneTool import AllowSendto
        except ImportError:
            print("WARNING: AllowSendto not given to Anonymous.")
        else:
            portal.manage_permission(AllowSendto, ("Anonymous",))

    def teardownPloneSite(self, portal):
        unpatch_mailhost(portal)


class FixesFixture(BasicFixture):
    # Fixture that loads fixes.zcml.  This activates the improved
    # templates and scripts.
    defaultBases = (PLONE_FIXTURE,)
    load_fixes = True

    def setUpZope(self, app, configurationContext):
        super(FixesFixture, self).setUpZope(app, configurationContext)
        # Load extra ZCML.
        import collective.honeypot

        self.loadZCML(package=collective.honeypot, name="fixes.zcml")


BASIC_FIXTURE = BasicFixture()
FIXES_FIXTURE = FixesFixture()
BASIC_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(BASIC_FIXTURE,), name="collective.honeypot:BasicFunctional",
)
FIXES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXES_FIXTURE,), name="collective.honeypot:FixesFunctional",
)
