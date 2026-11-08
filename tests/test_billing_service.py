import unittest

from app.services.billing_service import (
    calculate_request_amount,
    calculate_subscription_total,
)


class BillingServiceTest(unittest.TestCase):
    def setUp(self):
        self.subscription = {
            "request_price_credits": 2,
            "subscription_price_credits": 250,
        }

    def test_calculates_request_amount_in_whole_credits(self):
        amount = calculate_request_amount(self.subscription)
        self.assertEqual(amount, 2)
        self.assertIsInstance(amount, int)

    def test_calculates_total(self):
        self.assertEqual(calculate_subscription_total(self.subscription, 4), 254)


if __name__ == "__main__":
    unittest.main()
