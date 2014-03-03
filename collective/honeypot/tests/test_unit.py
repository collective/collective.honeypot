# -*- coding: utf-8 -*-

import unittest

from collective.honeypot.config import FORBIDDEN_HONEYPOT_FIELD
from collective.honeypot.config import REQUIRED_HONEYPOT_FIELD
from collective.honeypot.utils import found_honeypot


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
