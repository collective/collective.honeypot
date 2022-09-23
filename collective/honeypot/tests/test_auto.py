from collective.honeypot.auto import ProtectHoneyTransform
from collective.honeypot.testing import HONEYPOT_FUNCTIONAL_TESTING
from collective.honeypot.interfaces import IHoneypotDisabledForm
from zope.interface import alsoProvides, noLongerProvides

import unittest


class HoneypotTransformTestCase(unittest.TestCase):
    layer = HONEYPOT_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.request.response.setHeader("Content-Type", "text/html")
        self.request.REQUEST_METHOD = "POST"

    def tearDown(self):
        noLongerProvides(self.request, IHoneypotDisabledForm)

    def test_transform_add_field_in_form(self):
        transform = ProtectHoneyTransform(self.portal, self.request)
        result = transform.transform(
            [
                (
                    "<html>\n<body>"
                    '<form action="http://nohost/myaction" method="POST">'
                    "</form></body>\n</html>"
                )
            ],
            "utf-8",
        )
        self.assertTrue(b'name="protected_1"' in result.serialize())

    def test_transform_do_not_add_field_in_form_if_interface_provided(self):
        alsoProvides(self.request, IHoneypotDisabledForm)
        transform = ProtectHoneyTransform(self.portal, self.request)
        result = transform.transform(
            [
                (
                    "<html>\n<body>"
                    '<form action="http://nohost/myaction" method="POST">'
                    "</form></body>\n</html>"
                )
            ],
            "utf-8",
        )
        self.assertFalse(b'name="protected_1"' in result.serialize())
