# -*- coding: utf-8 -*-

import pkg_resources
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.tests.utils import MockMailHost
from Products.MailHost.interfaces import IMailHost
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from zope.component import getSiteManager
from zope.component import queryUtility

try:
    pkg_resources.get_distribution('plone.app.discussion')
except pkg_resources.DistributionNotFound:
    HAS_DISCUSSION = False
else:
    HAS_DISCUSSION = True
    from plone.app.discussion.interfaces import IDiscussionSettings
    from plone.registry.interfaces import IRegistry


def patch_mailhost(portal):
    portal._updateProperty('email_from_address', 'webmaster@example.org')
    portal._original_MailHost = portal.MailHost
    portal.MailHost = mailhost = MockMailHost('MailHost')
    mailhost.smtp_host = 'localhost'
    sm = getSiteManager(context=portal)
    sm.unregisterUtility(provided=IMailHost)
    sm.registerUtility(mailhost, provided=IMailHost)


def unpatch_mailhost(portal):
    portal.MailHost = portal._original_MailHost
    sm = getSiteManager(context=portal)
    sm.unregisterUtility(provided=IMailHost)
    sm.registerUtility(aq_base(portal._original_MailHost),
                       provided=IMailHost)


def enable_self_registration(portal):
    # Taken from plone.app.controlpanel
    app_perms = portal.rolesOfPermission(permission='Add portal member')
    reg_roles = []
    for appperm in app_perms:
        if appperm['selected'] == 'SELECTED':
            reg_roles.append(appperm['name'])
    if 'Anonymous' not in reg_roles:
        reg_roles.append('Anonymous')
    portal.manage_permission('Add portal member', roles=reg_roles,
                             acquire=0)


class BasicFixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.honeypot
        self.loadZCML(package=collective.honeypot)
        self.loadZCML(package=collective.honeypot, name='overrides.zcml')

    def setUpPloneSite(self, portal):
        patch_mailhost(portal)
        enable_self_registration(portal)
        if HAS_DISCUSSION:
            # Enable commenting.
            registry = queryUtility(IRegistry)
            settings = registry.forInterface(IDiscussionSettings)
            settings.globally_enabled = True
            settings.anonymous_comments = True
        # This is for old-style comments.  That should be only for
        # Plone 3 and 4.0, but the scripts are still available, so we
        # still need to protect them and test them
        types_tool = getToolByName(portal, 'portal_types')
        types_tool.Document.allow_discussion = True
        portal.manage_permission('Reply to item', ('Anonymous', ))

    def teardownPloneSite(self, portal):
        unpatch_mailhost(portal)


class FixesFixture(BasicFixture):
    # Fixture that loads fixes.zcml.  This activates the improved
    # templates and scripts.
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        super(FixesFixture, self).setUpZope(app, configurationContext)
        # Load extra ZCML
        import collective.honeypot
        self.loadZCML(package=collective.honeypot, name='fixes.zcml')


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
