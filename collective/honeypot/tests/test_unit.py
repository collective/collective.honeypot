# -*- coding: utf-8 -*-

import unittest

from Acquisition import Implicit
from Testing import makerequest
from collective.honeypot.config import HONEYPOT_FIELD
from collective.honeypot.utils import check_post
from collective.honeypot.utils import found_honeypot
from collective.honeypot.utils import get_form
from collective.honeypot.utils import whitelisted
from zope.publisher.browser import TestRequest
from zExceptions import Forbidden


class UtilsTestCase(unittest.TestCase):

    def test_found_honeypot(self):
        # 1. The honeypot field MUST be there if required is True.
        self.assertFalse(found_honeypot({}, required=False))
        self.assertEqual(found_honeypot({}, required=True),
                         'misses required field')
        # 2. The honeypot field MUST be empty.
        self.assertFalse(found_honeypot(
            {HONEYPOT_FIELD: ''}, required=False))
        self.assertFalse(found_honeypot(
            {HONEYPOT_FIELD: ''}, required=True))
        self.assertEqual(found_honeypot(
            {HONEYPOT_FIELD: 'hello'}, required=False),
            'has forbidden field')
        self.assertEqual(found_honeypot(
            {HONEYPOT_FIELD: 'hello'}, required=True),
            'has forbidden field')

    def test_get_form(self):
        # get_form gets the form fields, leaving out password fields.
        self.assertEqual(get_form({}), {})
        self.assertEqual(get_form({'foo': 'bar'}), {'foo': 'bar'})
        self.assertEqual(get_form(TestRequest()), {})
        self.assertEqual(get_form(TestRequest(form={'hoppa': 'kikoo'})),
                         {'hoppa': 'kikoo'})
        secret_request = TestRequest(
            form={'hoppa': 'kikoo',
                  'password': 'secret',
                  'password_confirm': 'secret2',
                  '__ac_password': 'secret3',
                  'somepasswordfield': 'secret4',
                  '__ac_name': 'admin',
                  })
        self.assertEqual(get_form(secret_request),
                         {'hoppa': 'kikoo', '__ac_name': 'admin'})
        # The stripped data should still be on the original form.
        self.assertEqual(secret_request.form['password'], 'secret')
        self.assertEqual(secret_request.form['password_confirm'], 'secret2')
        self.assertEqual(secret_request.form['__ac_password'], 'secret3')
        self.assertEqual(secret_request.form['somepasswordfield'], 'secret4')

    def _request(self, dest='', method='POST', form=None):
        # Return a proper request.  POST by default.
        context = Implicit()
        environ = {'REQUEST_METHOD': method, 'SCRIPT_NAME': dest}
        obj = makerequest.makerequest(context, environ=environ)
        request = obj.REQUEST
        if form is not None:
            request.form = form
        return request

    def test_check_post(self):
        self.assertEqual(check_post(TestRequest()), None)
        self.assertEqual(check_post(self._request(method='GET')), None)
        self.assertEqual(check_post(self._request()), None)
        # Post forbidden data to a protected form.
        request = self._request(dest='/join_form',
                                form={HONEYPOT_FIELD: 'bear'})
        self.assertRaises(Forbidden, check_post, request)
        # If it is a GET request, it is fine.
        request = self._request(dest='/join_form', method='GET',
                                form={HONEYPOT_FIELD: 'bear'})
        self.assertEqual(check_post(self._request()), None)
        # When the field is empty, this is fine.
        request = self._request(dest='/join_form',
                                form={HONEYPOT_FIELD: ''})
        self.assertEqual(check_post(self._request()), None)

    def test_whitelisted(self):
        self.assertEqual(whitelisted(''), False)
        self.assertEqual(whitelisted('random'), False)
        self.assertEqual(whitelisted('jq_reveal_email'), True)
        self.assertEqual(whitelisted('at_validate_field'), True)
        self.assertEqual(whitelisted('z3cform_validate_field'), True)
        # various jquery methods may use this
        self.assertEqual(whitelisted('jq_'), True)
        self.assertEqual(whitelisted('jq'), False)
        self.assertEqual(whitelisted('jq_foo_bar'), True)
        self.assertEqual(whitelisted('foo_jq_'), False)
