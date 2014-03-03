# -*- coding: utf-8 -*-

import unittest

from zope.publisher.browser import TestRequest
from collective.honeypot.config import FORBIDDEN_HONEYPOT_FIELD
from collective.honeypot.config import REQUIRED_HONEYPOT_FIELD
from collective.honeypot.utils import found_honeypot
from collective.honeypot.utils import get_form


class UtilsTestCase(unittest.TestCase):

    def test_found_honeypot(self):
        # 1. The required field MUST be there, but MAY be empty.
        # 2. The forbidden field MAY be there, but MUST be empty.
        self.assertEqual(found_honeypot({}), 'misses required field')
        self.assertFalse(found_honeypot(
            {REQUIRED_HONEYPOT_FIELD: ''}))
        self.assertEqual(found_honeypot(
            {FORBIDDEN_HONEYPOT_FIELD: ''}), 'misses required field')
        self.assertFalse(found_honeypot(
            {REQUIRED_HONEYPOT_FIELD: 'hello'}))
        self.assertFalse(found_honeypot(
            {REQUIRED_HONEYPOT_FIELD: '',
             FORBIDDEN_HONEYPOT_FIELD: ''}))
        self.assertEqual(found_honeypot(
            {REQUIRED_HONEYPOT_FIELD: '',
             FORBIDDEN_HONEYPOT_FIELD: 'hello'}), 'has forbidden field')
        self.assertEqual(found_honeypot(
            {REQUIRED_HONEYPOT_FIELD: 'hello',
             FORBIDDEN_HONEYPOT_FIELD: 'hello'}), 'has forbidden field')

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
                  '__ac_name': 'admin',
                  })
        self.assertEqual(get_form(secret_request),
            {'hoppa': 'kikoo', '__ac_name': 'admin'})
        # The stripped data should still be on the original form.
        self.assertEqual(secret_request.form['password'], 'secret')
        self.assertEqual(secret_request.form['password_confirm'], 'secret2')
        self.assertEqual(secret_request.form['__ac_password'], 'secret3')
