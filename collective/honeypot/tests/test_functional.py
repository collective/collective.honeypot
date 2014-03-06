# -*- coding: utf-8 -*-

import unittest
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.testing.z2 import Browser
from zExceptions import Forbidden

from collective.honeypot.testing import BASIC_FUNCTIONAL_TESTING
from collective.honeypot.testing import FIXES_FUNCTIONAL_TESTING


class BasicTestCase(unittest.TestCase):
    # This does NOT have our fixed templates and scripts activated.
    layer = BASIC_FUNCTIONAL_TESTING

    def setUp(self):
        app = self.layer['app']
        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        self.mailhost = self.portal.MailHost

    def test_subscriber(self):
        # Posting should trigger our event subscriber and do the
        # honeypot checks.
        self.browser.post(self.portal_url, 'innocent=true')
        self.assertRaises(Forbidden, self.browser.post,
                          self.portal_url, 'protected_1=asdfsd')
        # The subscriber is registered for the site root, but this
        # does not mean it only works for posts to the site root.
        # First create a folder.
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'f1', title=u"Folder 1")
        folder = self.portal.f1
        self.assertRaises(Forbidden, self.browser.post,
                          folder.absolute_url(),
                          'protected_1=asdfsd')
        self.assertRaises(Forbidden, self.browser.post,
                          self.portal_url + '/non-existing-page',
                          'protected_1=asdfsd')

    def test_sendto_empty(self):
        self.browser.open(self.portal_url + '/sendto_form')
        form = self.browser.getForm(name='sendto_form')
        form.submit()
        self.assertTrue('Please correct the indicated errors.'
                        in self.browser.contents)
        self.assertEqual(len(self.mailhost.messages), 0)

    def test_sendto_normal(self):
        self.browser.open(self.portal_url + '/sendto_form')
        form = self.browser.getForm(name='sendto_form')
        self.browser.getControl(name='send_to_address').value = 'joe@example.org'
        self.browser.getControl(name='send_from_address').value = 'spammer@example.org'
        self.browser.getControl(name='comment').value = 'Spam, bacon and eggs'
        form.submit()
        self.assertTrue('Please correct the indicated errors.'
                        not in self.browser.contents)
        self.assertEqual(len(self.mailhost.messages), 1)


class FixesTestCase(BasicTestCase):
    # This DOES have our fixed templates and scripts activated.
    layer = FIXES_FUNCTIONAL_TESTING
    # Note that we inherit the test methods from BasicTestCase, to
    # check that the standard forms still work, and override a few to
    # show that the honeypot field is present.

    def test_sendto_spammer(self):
        self.browser.open(self.portal_url + '/sendto_form')
        form = self.browser.getForm(name='sendto_form')
        self.browser.getControl(name='send_to_address').value = 'joe@example.org'
        self.browser.getControl(name='send_from_address').value = 'spammer@example.org'
        self.browser.getControl(name='comment').value = 'Spam, bacon and eggs'
        # Yummy, a honeypot!
        self.browser.getControl(name='protected_1').value = 'Spammity spam'
        self.assertRaises(Forbidden, form.submit)
        self.assertEqual(len(self.mailhost.messages), 0)

    def test_sendto_post(self):
        # Try a post without the honeypot field.
        self.assertRaises(Forbidden, self.browser.post,
                          self.portal_url + '/sendto_form', '')
        self.assertRaises(Forbidden, self.browser.post,
                          self.portal_url + '/sendto', '')
        self.assertEqual(len(self.mailhost.messages), 0)
