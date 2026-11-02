import unittest

from app.services.access_service import authorize_request
from app.services.subscription_service import validate_subscription_request


class FinalRulesTest(unittest.TestCase):
    def test_consumer_cannot_subscribe_to_own_api(self):
        allowed, _ = validate_subscription_request(
            {"id": 1}, {"provider_org_id": 1}, True, None
        )
        self.assertFalse(allowed)

    def test_premium_access_requires_premium_plan(self):
        allowed, _ = authorize_request(
            {"status": "active", "max_access_level": "basic"}, "premium"
        )
        self.assertFalse(allowed)


if __name__ == "__main__":
    unittest.main()
