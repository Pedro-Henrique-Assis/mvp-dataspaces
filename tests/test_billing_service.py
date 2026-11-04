import unittest
from decimal import Decimal

from app.services.billing_service import (
    calculate_request_amount,
    calculate_subscription_total,
)


class BillingServiceTest(unittest.TestCase):
    def setUp(self):
        self.subscription = {
            "request_price_usd": Decimal("0.20"),
            "subscription_price_usd": Decimal("25.00"),
        }

    def test_calculates_request_amount(self):
        self.assertEqual(calculate_request_amount(self.subscription), Decimal("0.20"))

    def test_calculates_total(self):
        self.assertEqual(
            calculate_subscription_total(self.subscription, Decimal("0.40")),
            Decimal("25.40"),
        )


if __name__ == "__main__":
    unittest.main()
