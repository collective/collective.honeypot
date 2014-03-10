# -*- coding: utf-8 -*-

import pkg_resources
import textwrap
import transaction
import unittest
import urllib
from collective.honeypot.testing import BASIC_FUNCTIONAL_TESTING
from collective.honeypot.testing import FIXES_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.testing.z2 import Browser
from zExceptions import Forbidden

try:
    pkg_resources.get_distribution('plone.app.discussion')
except pkg_resources.DistributionNotFound:
    HAS_DISCUSSION = False
else:
    HAS_DISCUSSION = True
    from plone.app.discussion.interfaces import IConversation


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
                          self.portal_url, 'protected_1=bad')
        # The subscriber is registered for the site root, but this
        # does not mean it only works for posts to the site root.
        # First create a folder.
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'f1', title=u"Folder 1")
        folder = self.portal.f1
        self.assertRaises(Forbidden, self.browser.post,
                          folder.absolute_url(),
                          'protected_1=bad')
        self.assertRaises(Forbidden, self.browser.post,
                          self.portal_url + '/non-existing-page',
                          'protected_1=bad')

    def test_authenticator(self):
        authenticator = self.layer['portal'].restrictedTraverse(
            '@@authenticator').authenticator()
        self.assertTrue(authenticator.startswith(
            '<input type="hidden" name="_authenticator" value='))
        self.assertTrue('protected' in authenticator)
        self.browser.open(self.portal_url + '/@@honeypot_field')
        self.assertTrue(self.browser.contents.strip() in authenticator)

    def test_honeypot_field_view(self):
        self.browser.open(self.portal_url + '/@@honeypot_field')
        text = textwrap.dedent("""
            <div style="display: none">
              <input type="text" value="" name="protected_1" />
            </div>""")
        self.assertEqual(self.browser.contents.strip(), text.strip())

    ### Tests for the sendto form.

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

    def test_sendto_post_honey(self):
        # Try a post with the honeypot field.
        self.assertRaises(Forbidden, self.browser.post,
                          self.portal_url + '/sendto_form', 'protected_1=bad')
        self.assertRaises(Forbidden, self.browser.post,
                          self.portal_url + '/sendto', 'protected_1=bad')
        self.assertEqual(len(self.mailhost.messages), 0)

    ### Tests for the contact-info form.

    def test_contact_info_empty(self):
        self.browser.open(self.portal_url + '/contact-info')
        form = self.browser.getForm(name='feedback_form')
        form.submit()
        self.assertTrue('Please correct the indicated errors.'
                        in self.browser.contents)
        self.assertEqual(len(self.mailhost.messages), 0)

    def test_contact_info_normal(self):
        self.browser.open(self.portal_url + '/contact-info')
        form = self.browser.getForm(name='feedback_form')
        self.browser.getControl(name='sender_fullname').value = 'Mr. Spammer'
        self.browser.getControl(name='sender_from_address').value = 'spammer@example.org'
        self.browser.getControl(name='subject').value = 'Spammmmmm'
        self.browser.getControl(name='message').value = 'Spam, bacon and eggs'
        form.submit()
        self.assertTrue('Please correct the indicated errors.'
                        not in self.browser.contents)
        self.assertEqual(len(self.mailhost.messages), 1)

    def test_contact_info_post_honey(self):
        # Try a post with the honeypot field.
        self.assertRaises(Forbidden, self.browser.post,
                          self.portal_url + '/contact-info', 'protected_1=bad')
        self.assertRaises(Forbidden, self.browser.post,
                          self.portal_url + '/send_feedback_site',
                          'protected_1=bad')
        self.assertEqual(len(self.mailhost.messages), 0)

    ### Tests for the register form.

    def test_register_empty(self):
        self.browser.open(self.portal_url + '/@@register')
        # We could get the form, but with this general id it seems a
        # bad idea:
        #form = self.browser.getForm(id='zc.page.browser_form')
        self.browser.getControl(name='form.actions.register').click()
        self.assertTrue('There were errors' in self.browser.contents)
        self.assertEqual(len(self.mailhost.messages), 0)

    def test_register_normal(self):
        self.browser.open(self.portal_url + '/@@register')
        self.browser.getControl(name='form.fullname').value = 'Mr. Spammer'
        self.browser.getControl(name='form.username').value = 'spammer'
        self.browser.getControl(name='form.email').value = 'spammer@example.org'
        self.browser.getControl(name='form.actions.register').click()
        self.assertTrue('There were errors' not in self.browser.contents)
        self.assertEqual(len(self.mailhost.messages), 1)

    def test_register_post_honey(self):
        # Try a post with the honeypot field.
        self.assertRaises(Forbidden, self.browser.post,
                          self.portal_url + '/@@register', 'protected_1=bad')
        self.assertRaises(Forbidden, self.browser.post,
                          self.portal_url + '/register', 'protected_1=bad')
        self.assertEqual(len(self.mailhost.messages), 0)

    ### Tests for the comment form.

    def _create_commentable_doc(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Document', 'doc', title=u"Document 1")
        self.portal.doc.allowDiscussion(True)
        # Need to commit, otherwise the browser does not see it.
        transaction.commit()

    if HAS_DISCUSSION:

        def test_discussion_empty(self):
            self._create_commentable_doc()
            self.browser.open(self.portal_url + '/doc')
            self.browser.getControl(name='form.buttons.comment').click()
            self.assertTrue('Required input is missing.' in self.browser.contents)
            self.assertEqual(len(self.mailhost.messages), 0)

        def test_discussion_normal(self):
            self._create_commentable_doc()
            self.browser.open(self.portal_url + '/doc')
            self.browser.getControl(name='form.widgets.author_name').value = 'Mr. Spammer'
            self.browser.getControl(name='form.widgets.text').value = 'Spam spam.'
            self.browser.getControl(name='form.buttons.comment').click()
            self.assertTrue('Required input is missing.' not in self.browser.contents)
            # The comment is added.
            conversation = IConversation(self.portal.doc)
            self.assertEqual(len(list(conversation.getComments())), 1)
            # No mails are sent.
            self.assertEqual(len(self.mailhost.messages), 0)

        def test_discussion_post_honey(self):
            # Try a post with the honeypot field.
            self.assertRaises(Forbidden, self.browser.post,
                              self.portal_url + '/doc', 'protected_1=bad')
            self.assertEqual(len(self.mailhost.messages), 0)

    if not HAS_DISCUSSION:

        def test_comment_empty(self):
            self._create_commentable_doc()
            self.browser.open(self.portal_url + '/doc')
            self.browser.getControl('Add Comment').click()
            self.assertEqual(self.browser.url,
                             self.portal_url + '/doc/discussion_reply_form')
            form = self.browser.getForm(name='edit_form')
            form.submit()
            self.assertTrue('Please correct the indicated errors.'
                            in self.browser.contents)
            self.assertTrue('Comment cannot be blank.'
                            in self.browser.contents)
            self.assertEqual(len(self.mailhost.messages), 0)

        def test_comment_normal(self):
            self._create_commentable_doc()
            self.browser.open(self.portal_url + '/doc/discussion_reply_form')
            form = self.browser.getForm(name='edit_form')
            self.browser.getControl(name='body_text').value = 'Spammerdespam'
            form.submit()
            self.assertTrue('Please correct the indicated errors.'
                            not in self.browser.contents)
            self.assertTrue('Comment added.' in self.browser.contents)
            # The comment is added.
            self.assertEqual(len(self.portal.doc.talkback.getReplies()), 1)
            # No mails are sent.
            self.assertEqual(len(self.mailhost.messages), 0)

        def test_comment_post_honey(self):
            # Try a post with the honeypot field.
            self.assertRaises(Forbidden, self.browser.post,
                              self.portal_url + '/doc/discussion_reply_form',
                              'protected_1=bad')
            self.assertEqual(len(self.mailhost.messages), 0)
            self.assertRaises(Forbidden, self.browser.post,
                              self.portal_url + '/doc/discussion_reply',
                              'protected_1=bad')
            self.assertEqual(len(self.mailhost.messages), 0)


class FixesTestCase(BasicTestCase):
    # This DOES have our fixed templates and scripts activated.
    layer = FIXES_FUNCTIONAL_TESTING
    # Note that we inherit the test methods from BasicTestCase, to
    # check that the standard forms still work, and override a few to
    # show that the honeypot field is present.

    ### Tests for the sendto form.

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

    def test_sendto_post_no_honey(self):
        # Try a post without the honeypot field.
        self.assertRaises(Forbidden, self.browser.post,
                          self.portal_url + '/sendto_form', '')
        self.assertRaises(Forbidden, self.browser.post,
                          self.portal_url + '/sendto', '')
        self.assertEqual(len(self.mailhost.messages), 0)

    def test_sendto_get(self):
        # Try a GET.  This does not trigger our honeypot checks, but
        # still it should not result in the sending of an email.
        qs = urllib.urlencode({
            'send_to_address': 'joe@example.org',
            'send_from_address': 'spammer@example.org',
            'comment': 'Spam, bacon and eggs'})
        self.browser.open(self.portal_url + '/sendto_form?' + qs)
        self.assertEqual(len(self.mailhost.messages), 0)
        # POST is required for the final script.
        self.assertRaises(Forbidden, self.browser.open,
                          self.portal_url + '/sendto?' + qs)
        self.assertEqual(len(self.mailhost.messages), 0)

    ### Tests for the contact-info form.

    def test_contact_info_spammer(self):
        self.browser.open(self.portal_url + '/contact-info')
        form = self.browser.getForm(name='feedback_form')
        self.browser.getControl(name='sender_fullname').value = 'Mr. Spammer'
        self.browser.getControl(name='sender_from_address').value = 'spammer@example.org'
        self.browser.getControl(name='subject').value = 'Spammmmmm'
        self.browser.getControl(name='message').value = 'Spam, bacon and eggs'
        # Yummy, a honeypot!
        self.browser.getControl(name='protected_1').value = 'Spammity spam'
        self.assertRaises(Forbidden, form.submit)
        self.assertEqual(len(self.mailhost.messages), 0)

    def test_contact_info_post_no_honey(self):
        # Try a post without the honeypot field.
        self.assertRaises(Forbidden, self.browser.post,
                          self.portal_url + '/contact-info', '')
        self.assertRaises(Forbidden, self.browser.post,
                          self.portal_url + '/send_feedback_site', '')
        self.assertEqual(len(self.mailhost.messages), 0)

    def test_contact_info_get(self):
        # Try a GET.  This does not trigger our honeypot checks, but
        # still it should not result in the sending of an email.
        qs = urllib.urlencode({
            'sender_fullname': 'Mr. Spammer',
            'sender_from_address': 'spammer@example.org',
            'subject': 'Spammmmmm',
            'message': 'Spam, bacon and eggs'})
        self.browser.open(self.portal_url + '/contact-info?' + qs)
        self.assertEqual(len(self.mailhost.messages), 0)
        # POST is required for the final script.
        self.assertRaises(Forbidden, self.browser.open,
                          self.portal_url + '/send_feedback_site?' + qs)
        self.assertEqual(len(self.mailhost.messages), 0)

    ### Tests for the register form.

    def test_register_spammer(self):
        self.browser.open(self.portal_url + '/@@register')
        self.browser.getControl(name='form.fullname').value = 'Mr. Spammer'
        self.browser.getControl(name='form.username').value = 'spammer'
        self.browser.getControl(name='form.email').value = 'spammer@example.org'
        # Yummy, a honeypot!
        self.browser.getControl(name='protected_1', index=0).value = 'Spammity spam'
        register_button = self.browser.getControl(name='form.actions.register')
        self.assertRaises(Forbidden, register_button.click)
        self.assertEqual(len(self.mailhost.messages), 0)

    def test_register_post_no_honey(self):
        # Try a post without the honeypot field.
        self.assertRaises(Forbidden, self.browser.post,
                          self.portal_url + '/@@register', '')
        self.assertRaises(Forbidden, self.browser.post,
                          self.portal_url + '/register', '')
        self.assertEqual(len(self.mailhost.messages), 0)

    ### Tests for the comment form.

    if HAS_DISCUSSION:

        def test_discussion_spammer(self):
            self._create_commentable_doc()
            self.browser.open(self.portal_url + '/doc')
            self.browser.getControl(name='form.widgets.author_name').value = 'Mr. Spammer'
            self.browser.getControl(name='form.widgets.text').value = 'Spam spam.'
            # Yummy, a honeypot!
            self.browser.getControl(name='protected_1', index=0).value = 'Spammity spam'
            button = self.browser.getControl(name='form.buttons.comment')
            self.assertRaises(Forbidden, button.click)
            self.assertEqual(len(self.mailhost.messages), 0)

        # Note: we do not try a post without the honeypot field, because
        # there is no special action that the form posts to: it simply
        # posts to the current view, and we cannot explicitly protect all
        # views.

    if not HAS_DISCUSSION:

        def test_comment_spammer(self):
            self._create_commentable_doc()
            self.browser.open(self.portal_url + '/doc/discussion_reply_form')
            form = self.browser.getForm(name='edit_form')
            self.browser.getControl(name='body_text').value = 'Spammerdespam'
            # Yummy, a honeypot!
            self.browser.getControl(name='protected_1', index=0).value = 'Spammity spam'
            self.assertRaises(Forbidden, form.submit)
            self.assertEqual(len(self.mailhost.messages), 0)

        def test_comment_post_no_honey(self):
            # Try a post without the honeypot field.
            self._create_commentable_doc()
            self.assertRaises(Forbidden, self.browser.post,
                              self.portal_url + '/doc/discussion_reply_form', '')
            self.assertEqual(len(self.mailhost.messages), 0)
            self.assertRaises(Forbidden, self.browser.post,
                              self.portal_url + '/doc/discussion_reply', '')
            self.assertEqual(len(self.mailhost.messages), 0)

        def test_comment_get(self):
            # Try a GET.  This does not trigger our honeypot checks, but
            # still it should not result in the sending of an email.
            self._create_commentable_doc()
            qs = urllib.urlencode({
                'body_text': 'Spam, bacon and eggs',
                'subject': 'Spam'})
            self.browser.open(self.portal_url + '/doc/discussion_reply_form?' + qs)
            self.assertEqual(len(self.mailhost.messages), 0)
            # POST is required for the final script.
            self.assertRaises(Forbidden, self.browser.open,
                              self.portal_url + '/doc/discussion_reply?' + qs)
            self.assertEqual(len(self.mailhost.messages), 0)
