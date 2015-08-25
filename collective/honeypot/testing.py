# -*- coding: utf-8 -*-

import collective.honeypot.config
import pkg_resources
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.tests.utils import MockMailHost
from Products.MailHost.interfaces import IMailHost
from persistent.list import PersistentList
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.testing import z2
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

try:
    pkg_resources.get_distribution('plone.app.users')
except pkg_resources.DistributionNotFound:
    HAS_REGISTER_FORM = False
else:
    HAS_REGISTER_FORM = True

try:
    pkg_resources.get_distribution('quintagroup.plonecomments')
except pkg_resources.DistributionNotFound:
    HAS_QUINTA = False
else:
    HAS_QUINTA = True

# We want WHITELISTED_START to be empty by default currently, but we
# do want to test it.
start = list(collective.honeypot.config.WHITELISTED_START)
start.append('jq_')
collective.honeypot.config.WHITELISTED_START = set(start)


class BetterMockMailHost(MockMailHost):

    def reset(self):
        # Somehow on Plone 3 it is necessary to use a persistent list
        # instead of a normal list.
        self.messages = PersistentList()


def patch_mailhost(portal):
    portal._updateProperty('email_from_address', 'webmaster@example.org')
    portal._original_MailHost = portal.MailHost
    portal.MailHost = mailhost = BetterMockMailHost('MailHost')
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


def isDiscussionAllowedFor(obj):
    return True


class BasicFixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.honeypot
        self.loadZCML(package=collective.honeypot)
        self.loadZCML(package=collective.honeypot, name='overrides.zcml')
        # Install product and call its initialize() function
        z2.installProduct(app, 'collective.honeypot')
        if HAS_QUINTA:
            import quintagroup.plonecomments
            self.loadZCML(package=quintagroup.plonecomments)

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'collective.honeypot')

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
        if hasattr(Products.GenericSetup.zcml, '_profile_regs'):
            for profile in (u'quintagroup.plonecomments:default',
                            u'quintagroup.plonecomments:uninstall'):
                if profile not in Products.GenericSetup.zcml._profile_regs:
                    continue
                Products.GenericSetup.zcml._profile_regs.remove(profile)

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

        # Allow anonymous to the sendto form.  This is disallowed in
        # Plone 4.3.3.
        from Products.CMFPlone.PloneTool import AllowSendto
        portal.manage_permission(AllowSendto, ('Anonymous', ))

        # In Plone 4.1 the old validate_talkback script goes wrong
        # because the discussion tool does not have a
        # isDiscussionAllowedFor method.  Let's fix that with a dummy
        # one.  Note that getToolByName(portal, 'portal_discussion')
        # gets the old commenting tool and portal.portal_discussion
        # gets the new p.a.discussion tool, which lacks this method.
        # Go figure.
        discussion_tool = portal.portal_discussion
        if not hasattr(discussion_tool, 'isDiscussionAllowedFor'):
            discussion_tool.isDiscussionAllowedFor = isDiscussionAllowedFor

        if not hasattr(portal, 'portal_feedback'):
            # send_feedback does not work without a portal_feedback.
            # Probably fine.  We add an object without caring what it
            # really is.
            portal.portal_feedback = portal.portal_discussion

    def teardownPloneSite(self, portal):
        unpatch_mailhost(portal)


class ProfileFixture(BasicFixture):
    # Fixture that applies our GenericSetup profile.  This activates
    # the improved templates and scripts.  This is the recommended way
    # on Plone 3, but is expected to work on Plone 4 as well.
    defaultBases = (PLONE_FIXTURE,)
    load_fixes = False

    def setUpPloneSite(self, portal):
        super(ProfileFixture, self).setUpPloneSite(portal)
        applyProfile(portal, 'collective.honeypot:default')


class FixesFixture(BasicFixture):
    # Fixture that loads fixes.zcml.  This activates the improved
    # templates and scripts.  This is the recommended way
    # on Plone 4, but is expected to work on Plone 3 as well.
    defaultBases = (PLONE_FIXTURE,)
    load_fixes = True

    def setUpZope(self, app, configurationContext):
        super(FixesFixture, self).setUpZope(app, configurationContext)
        # Load extra ZCML.
        import collective.honeypot
        self.loadZCML(package=collective.honeypot, name='fixes.zcml')


BASIC_FIXTURE = BasicFixture()
FIXES_FIXTURE = FixesFixture()
PROFILE_FIXTURE = ProfileFixture()
BASIC_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(BASIC_FIXTURE,),
    name='collective.honeypot:BasicFunctional',
)
FIXES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXES_FIXTURE,),
    name='collective.honeypot:FixesFunctional',
)
PROFILE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PROFILE_FIXTURE,),
    name='collective.honeypot:ProfileFunctional',
)
