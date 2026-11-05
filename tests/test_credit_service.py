import re
import unittest
from decimal import Decimal
from unittest.mock import patch

from app.services import credit_service
from app.services.credit_service import fake_pix_code, open_top_up, package_price_usd, validate_package


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


class OpenTopUpTest(unittest.TestCase):
    def setUp(self):
        for name in ["expire_overdue", "find_open", "create"]:
            patcher = patch.object(credit_service, name)
            setattr(self, name, patcher.start())
            self.addCleanup(patcher.stop)

    def open(self, value="500"):
        return open_top_up(2, value, PACKAGES, Decimal("0.10"), 15)

    def test_open_top_up_reuses_pending_charge(self):
        self.find_open.return_value = "ABC"
        self.assertEqual(self.open(), (True, "ABC"))
        self.create.assert_not_called()

    def test_open_top_up_creates_charge_when_none_is_open(self):
        self.find_open.return_value = None
        valid, code = self.open()
        self.assertTrue(valid)
        self.create.assert_called_once_with(2, code, 500, Decimal("50.00"), 15)

    def test_open_top_up_rejects_invalid_package(self):
        for value in ["999999", "", None]:
            self.assertEqual(self.open(value), INVALID)
        self.expire_overdue.assert_not_called()

    def test_open_top_up_filters_by_package(self):
        self.find_open.return_value = "ABC"
        self.open("1000")
        self.find_open.assert_called_once_with(2, 1000)


if __name__ == "__main__":
    unittest.main()
