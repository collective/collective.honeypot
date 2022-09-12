# -*- coding: utf-8 -*-
from collective.honeypot.testing import HONEYPOT_API_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.restapi.testing import RelativeSession
from zExceptions import Forbidden

import transaction
import unittest


class HoneypotRestApiTestCase(unittest.TestCase):
    layer = HONEYPOT_API_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def test_restapi_protected_endpoint(self):
        """
        @email-notification use sendto_form Plone view that is patched in this package
        """
        response = self.api_session.post(
            self.portal_url + "/@email-notification",
            json={
                "from": "john@doe.com",
                "message": "Just want to say hi.",
            },
        )

        self.assertEqual(response.status_code, 204)

        response = self.api_session.post(
            self.portal_url + "/@email-notification",
            json={
                "from": "john@doe.com",
                "message": "Just want to say hi.",
                "protected_1": "foo",
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_restapi_general_post_protected(self):
        response = self.api_session.post(
            self.portal_url + "/@email-send",
            json={
                "to": "jane@doe.com",
                "from": "john@doe.com",
                "message": "Just want to say hi.",
            },
        )

        self.assertEqual(response.status_code, 204)

        response = self.api_session.post(
            self.portal_url + "/@email-send",
            json={
                "to": "jane@doe.com",
                "from": "john@doe.com",
                "message": "Just want to say hi.",
                "protected_1": "foo",
            },
        )
        self.assertEqual(response.status_code, 403)
