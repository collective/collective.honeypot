# -*- coding: utf-8 -*-

from collective.honeypot.testing import BASIC_FUNCTIONAL_TESTING
from collective.honeypot.testing import FIXES_FUNCTIONAL_TESTING
from plone.app.discussion.interfaces import IConversation
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing.z2 import Browser
from Products.CMFPlone.utils import getFSVersionTuple
from zExceptions import Forbidden
from zope.component import getMultiAdapter

import six.moves.urllib.error
import six.moves.urllib.parse
import six.moves.urllib.request
import textwrap
import transaction
import unittest


class BaseTestCase(unittest.TestCase):
    # Base test case class with a few extra methods and a standard
    # setup.

    def setUp(self):
        app = self.layer["app"]
        self.browser = Browser(app)
        self.browser.handleErrors = False
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.mailhost = self.portal.MailHost

    def _create_commentable_doc(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.portal.invokeFactory("Document", "doc", title=u"Document 1")
        self.portal.doc.allow_discussion = True
        # Need to commit, otherwise the browser does not see it.
        transaction.commit()

    def assertRaises(self, excClass, callableObj, *args, **kwargs):
        error_log = self.portal.error_log
        # Remove all error_log entries so we do not run into the
        # standard limit of 20 stored errors.
        while len(error_log.getLogEntries()) > 0:
            error_log.forgetEntry(error_log.getLogEntries()[-1]["id"])

        super(BaseTestCase, self).assertRaises(excClass, callableObj, *args, **kwargs)

    def login(self):
        self.browser.open(self.portal_url + "/login_form")
        self.browser.getControl(name="__ac_name").value = TEST_USER_NAME
        self.browser.getControl(name="__ac_password").value = TEST_USER_PASSWORD
        self.browser.getControl("Log in").click()


class StandardTestCase(BaseTestCase):
    # This does NOT have our fixed templates and scripts activated.
    layer = BASIC_FUNCTIONAL_TESTING

    def test_subscriber(self):
        # Posting should trigger our event subscriber and do the
        # honeypot checks.
        self.browser.post(self.portal_url, "innocent=true")
        self.assertRaises(
            Forbidden, self.browser.post, self.portal_url, "protected_1=bad"
        )
        # The subscriber is registered for the site root, but this
        # does not mean it only works for posts to the site root.
        # First create a folder.
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        self.portal.invokeFactory("Folder", "f1", title=u"Folder 1")
        folder = self.portal.f1
        self.assertRaises(
            Forbidden, self.browser.post, folder.absolute_url(), "protected_1=bad"
        )
        self.assertRaises(
            Forbidden,
            self.browser.post,
            self.portal_url + "/non-existing-page",
            "protected_1=bad",
        )

    def test_honeypot_field_view(self):
        portal = self.layer["portal"]
        honeypot = getMultiAdapter((portal, portal.REQUEST), name="honeypot_field")()
        text = textwrap.dedent(
            """
            <div style="display: none">
              <input type="text" value="" name="protected_1" />
            </div>"""
        )
        self.assertEqual(honeypot.strip(), text.strip())

    # Tests for the sendto form.

    def test_sendto_empty(self):
        self.login()
        self.browser.open(self.portal_url + "/sendto_form")
        self.browser.getControl(name="form.buttons.send").click()
        self.assertTrue("There were some errors." in self.browser.contents)
        self.assertEqual(len(self.mailhost.messages), 0)

    def test_sendto_normal(self):
        self.login()
        self.browser.open(self.portal_url + "/sendto_form")
        self.browser.getControl(
            name="form.widgets.send_to_address"
        ).value = "joe@example.org"
        self.browser.getControl(
            name="form.widgets.send_from_address"
        ).value = "spammer@example.org"
        self.browser.getControl(
            name="form.widgets.comment"
        ).value = "Spam, bacon and eggs"
        self.browser.getControl(name="form.buttons.send").click()
        self.assertTrue(
            "There were some errors." not in self.browser.contents
        )
        self.assertEqual(len(self.mailhost.messages), 1)

    def test_sendto_post_honey(self):
        self.login()
        # Try a post with the honeypot field.
        self.assertRaises(
            Forbidden,
            self.browser.post,
            self.portal_url + "/sendto_form",
            "protected_1=bad",
        )
        self.assertRaises(
            Forbidden, self.browser.post, self.portal_url + "/sendto", "protected_1=bad"
        )
        self.assertEqual(len(self.mailhost.messages), 0)

    def test_sendto_spammer(self):  # UNIQUE
        self.login()
        self.browser.open(self.portal_url + "/sendto_form")
        form = self.browser.getForm(id="form")
        self.browser.getControl(
            name="form.widgets.send_to_address"
        ).value = "joe@example.org"
        self.browser.getControl(
            name="form.widgets.send_from_address"
        ).value = "spammer@example.org"
        self.browser.getControl(
            name="form.widgets.comment"
        ).value = "Spam, bacon and eggs"
        # Yummy, a honeypot!
        self.browser.getControl(name="protected_1").value = "Spammity spam"
        self.assertRaises(Forbidden, form.submit)
        self.assertEqual(len(self.mailhost.messages), 0)

    def test_sendto_get(self):
        self.login()
        # Try a GET.  This does not trigger our honeypot checks, but
        # still it should not result in the sending of an email.
        qs = six.moves.urllib.parse.urlencode(
            {
                "send_to_address": "joe@example.org",
                "send_from_address": "spammer@example.org",
                "comment": "Spam, bacon and eggs",
            }
        )
        self.browser.open(self.portal_url + "/sendto_form?" + qs)
        self.assertEqual(len(self.mailhost.messages), 0)

    # Tests for the contact-info form.

    def test_contact_info_empty(self):
        self.browser.open(self.portal_url + "/contact-info")
        form = self.browser.getForm(action="contact-info")
        form.submit(name="form.buttons.send")
        self.assertTrue("There were some errors." in self.browser.contents)
        self.assertEqual(len(self.mailhost.messages), 0)

    def test_contact_info_normal(self):
        self.browser.open(self.portal_url + "/contact-info")
        self.browser.getControl(
            name="form.widgets.sender_fullname"
        ).value = "Mr. Spammer"
        self.browser.getControl(
            name="form.widgets.sender_from_address"
        ).value = "spammer@example.org"
        self.browser.getControl(name="form.widgets.subject").value = "Spammmmmm"
        self.browser.getControl(
            name="form.widgets.message"
        ).value = "Spam, bacon and eggs"
        form = self.browser.getForm(action="contact-info")
        form.submit(name="form.buttons.send")
        self.assertTrue("There were some errors." not in self.browser.contents)
        self.assertEqual(len(self.mailhost.messages), 1)

    def test_contact_info_post_honey(self):
        # Try a post with the honeypot field.
        self.assertRaises(
            Forbidden,
            self.browser.post,
            self.portal_url + "/contact-info",
            "protected_1=bad",
        )
        self.assertEqual(len(self.mailhost.messages), 0)

    def test_contact_info_spammer(self):
        self.browser.open(self.portal_url + "/contact-info")
        self.browser.getControl(
            name="form.widgets.sender_fullname"
        ).value = "Mr. Spammer"
        self.browser.getControl(
            name="form.widgets.sender_from_address"
        ).value = "spammer@example.org"
        self.browser.getControl(name="form.widgets.subject").value = "Spammmmmm"
        self.browser.getControl(
            name="form.widgets.message"
        ).value = "Spam, bacon and eggs"
        # Yummy, a honeypot!
        self.browser.getControl(name="protected_1").value = "Spammity spam"
        form = self.browser.getForm(action="contact-info")
        self.assertRaises(Forbidden, form.submit, name="form.buttons.send")
        self.assertEqual(len(self.mailhost.messages), 0)

    def test_contact_info_get(self):
        # Try a GET.  This does not trigger our honeypot checks, but
        # still it should not result in the sending of an email.
        qs = six.moves.urllib.parse.urlencode(
            {
                "sender_fullname": "Mr. Spammer",
                "sender_from_address": "spammer@example.org",
                "subject": "Spammmmmm",
                "message": "Spam, bacon and eggs",
            }
        )
        self.browser.open(self.portal_url + "/contact-info?" + qs)
        self.assertEqual(len(self.mailhost.messages), 0)

    # Tests for the register form.

    def test_register_empty(self):
        self.browser.open(self.portal_url + "/@@register")
        # We could get the form, but with this general id it seems a
        # bad idea:
        # form = self.browser.getForm(id='zc.page.browser_form')
        self.browser.getControl(name="form.buttons.register").click()
        self.assertTrue("There were errors" in self.browser.contents)
        self.assertEqual(len(self.mailhost.messages), 0)

    def test_register_normal(self):
        self.browser.open(self.portal_url + "/@@register")
        self.browser.getControl(name="form.widgets.fullname").value = "Mr. Spammer"
        self.browser.getControl(name="form.widgets.username").value = "spammer"
        self.browser.getControl(name="form.widgets.email").value = "spammer@example.org"
        self.browser.getControl(name="form.buttons.register").click()
        self.assertTrue("There were errors" not in self.browser.contents)
        self.assertEqual(len(self.mailhost.messages), 1)

    def test_register_post_honey(self):
        # Try a post with the honeypot field.
        self.assertRaises(
            Forbidden,
            self.browser.post,
            self.portal_url + "/@@register",
            "protected_1=bad",
        )
        self.assertRaises(
            Forbidden,
            self.browser.post,
            self.portal_url + "/register",
            "protected_1=bad",
        )
        self.assertEqual(len(self.mailhost.messages), 0)

    def test_register_spammer(self):
        self.browser.open(self.portal_url + "/@@register")
        self.browser.getControl(name="form.widgets.fullname").value = "Mr. Spammer"
        self.browser.getControl(name="form.widgets.username").value = "spammer"
        self.browser.getControl(name="form.widgets.email").value = "spammer@example.org"
        # Yummy, a honeypot!
        self.browser.getControl(name="protected_1", index=0).value = "Spammity spam"
        register_button = self.browser.getControl(name="form.buttons.register")
        self.assertRaises(Forbidden, register_button.click)
        self.assertEqual(len(self.mailhost.messages), 0)

    # Tests for the comment form.

    def test_discussion_empty(self):
        self._create_commentable_doc()
        self.browser.open(self.portal_url + "/doc")
        self.browser.getControl(name="form.buttons.comment").click()
        self.assertTrue("Required input is missing." in self.browser.contents)
        self.assertEqual(len(self.mailhost.messages), 0)

    def test_discussion_normal(self):
        self._create_commentable_doc()
        self.browser.open(self.portal_url + "/doc")
        self.browser.getControl(name="form.widgets.author_name").value = "Mr. Spammer"
        self.browser.getControl(name="form.widgets.text").value = "Spam spam."
        self.browser.getControl(name="form.buttons.comment").click()
        self.assertTrue("Required input is missing." not in self.browser.contents)
        # The comment is added.
        conversation = IConversation(self.portal.doc)
        self.assertEqual(len(list(conversation.getComments())), 1)
        # No mails are sent.
        self.assertEqual(len(self.mailhost.messages), 0)

    def test_discussion_post_honey(self):
        # Try a post with the honeypot field.
        self.assertRaises(
            Forbidden, self.browser.post, self.portal_url + "/doc", "protected_1=bad",
        )
        self.assertEqual(len(self.mailhost.messages), 0)


class FixesTestCase(BaseTestCase):
    # This has our fixes.zcml applied.  We run the same tests as our
    # base class.
    layer = FIXES_FUNCTIONAL_TESTING

    def test_sendto_post_no_honey(self):
        self.login()
        # Try a post without the honeypot field.
        self.assertRaises(
            Forbidden, self.browser.post, self.portal_url + "/sendto_form", ""
        )
        self.assertRaises(Forbidden, self.browser.post, self.portal_url + "/sendto", "")
        self.assertEqual(len(self.mailhost.messages), 0)

    def test_contact_info_post_no_honey(self):
        # Try a post without the honeypot field.
        self.assertRaises(
            Forbidden, self.browser.post, self.portal_url + "/contact-info", ""
        )
        self.assertEqual(len(self.mailhost.messages), 0)

    def test_register_post_no_honey(self):
        # Try a post without the honeypot field.
        self.assertRaises(
            Forbidden, self.browser.post, self.portal_url + "/@@register", ""
        )
        self.assertRaises(
            Forbidden, self.browser.post, self.portal_url + "/register", ""
        )
        self.assertEqual(len(self.mailhost.messages), 0)

    def test_discussion_spammer(self):
        self._create_commentable_doc()
        self.browser.open(self.portal_url + "/doc")
        self.browser.getControl(name="form.widgets.author_name").value = "Mr. Spammer"
        self.browser.getControl(name="form.widgets.text").value = "Spam spam."
        # Yummy, a honeypot!
        self.browser.getControl(name="protected_1", index=0).value = "Spammity spam"
        button = self.browser.getControl(name="form.buttons.comment")
        self.assertRaises(Forbidden, button.click)
        self.assertEqual(len(self.mailhost.messages), 0)
