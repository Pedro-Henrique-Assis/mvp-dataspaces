import re
import unittest
from decimal import Decimal

from app.services.credit_service import fake_pix_code, package_price_usd, validate_package


class PackagePriceTest(unittest.TestCase):
    def test_price_is_credits_times_credit_value(self):
        self.assertEqual(package_price_usd(500, Decimal("0.10")), Decimal("50.00"))
        self.assertEqual(package_price_usd(2500, Decimal("0.10")), Decimal("250.00"))


PACKAGES = (500, 1000, 2500)
INVALID = (False, "Pacote de créditos inválido.")


class ValidatePackageTest(unittest.TestCase):
    def test_accepts_package_from_the_list(self):
        self.assertEqual(validate_package("1000", PACKAGES), (True, 1000))

    def test_accepts_integer_value(self):
        self.assertEqual(validate_package(500, PACKAGES), (True, 500))

    def test_rejects_value_outside_the_list(self):
        self.assertEqual(validate_package("999999", PACKAGES), INVALID)
        self.assertEqual(validate_package("501", PACKAGES), INVALID)

    def test_rejects_text_and_empty_values(self):
        for value in ["abc", "", None, "5e2", "500.5"]:
            self.assertEqual(validate_package(value, PACKAGES), INVALID, value)

    def test_rejects_negative_and_zero(self):
        for value in ["-500", "0", -500]:
            self.assertEqual(validate_package(value, PACKAGES), INVALID, value)


class FakePixCodeTest(unittest.TestCase):
    def test_code_has_simulation_format(self):
        code = fake_pix_code(2, 500)
        self.assertRegex(code, r"^00020126SIMULACAO-DATASPACE-2-500-[0-9A-F]{8}$")

    def test_each_code_is_different(self):
        self.assertNotEqual(fake_pix_code(2, 500), fake_pix_code(2, 500))


if __name__ == "__main__":
    unittest.main()
