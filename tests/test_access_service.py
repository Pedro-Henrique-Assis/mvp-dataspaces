import unittest

from app.services.access_service import authorize_request


class AccessServiceTest(unittest.TestCase):
    def test_simple_plan_allows_basic(self):
        subscription = {"status": "active", "max_access_level": "basic"}
        allowed, _ = authorize_request(subscription, "basic")
        self.assertTrue(allowed)

    def test_simple_plan_rejects_premium(self):
        subscription = {"status": "active", "max_access_level": "basic"}
        allowed, _ = authorize_request(subscription, "premium")
        self.assertFalse(allowed)

    def test_premium_plan_allows_premium(self):
        subscription = {"status": "active", "max_access_level": "premium"}
        allowed, _ = authorize_request(subscription, "premium")
        self.assertTrue(allowed)