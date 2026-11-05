import unittest
from decimal import Decimal

from app.services.credit_service import package_price_usd


class PackagePriceTest(unittest.TestCase):
    def test_price_is_credits_times_credit_value(self):
        self.assertEqual(package_price_usd(500, Decimal("0.10")), Decimal("50.00"))
        self.assertEqual(package_price_usd(2500, Decimal("0.10")), Decimal("250.00"))


if __name__ == "__main__":
    unittest.main()
