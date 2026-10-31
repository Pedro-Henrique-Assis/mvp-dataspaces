import unittest

from app.services.subscription_service import validate_subscription_request


class SubscriptionServiceTest(unittest.TestCase):
    def setUp(self):
        self.consumer = {"id": 2}
        self.api = {"provider_org_id": 1}

    def test_allows_new_subscription(self):
        valid, _ = validate_subscription_request(self.consumer, self.api, True, None)
        self.assertTrue(valid)

    def test_rejects_own_api(self):
        valid, _ = validate_subscription_request({"id": 1}, self.api, True, None)
        self.assertFalse(valid)

    def test_rejects_duplicate(self):
        valid, _ = validate_subscription_request(self.consumer, self.api, True, {"id": 9})
        self.assertFalse(valid)


if __name__ == "__main__":
    unittest.main()