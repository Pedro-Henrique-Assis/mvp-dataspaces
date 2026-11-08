import re
import unittest
from decimal import Decimal
from unittest.mock import patch

from app.services import credit_service
from app.services.credit_service import (
    confirm_top_up,
    count_pages,
    fake_pix_code,
    open_top_up,
    package_price_usd,
    parse_page,
    validate_package,
)


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


class ConfirmTopUpTest(unittest.TestCase):
    def setUp(self):
        for name in ["expire_overdue", "get_by_code", "confirm"]:
            patcher = patch.object(credit_service, name)
            setattr(self, name, patcher.start())
            self.addCleanup(patcher.stop)
        self.get_by_code.return_value = {"credits": 500}

    def test_confirm_top_up_messages(self):
        cases = {
            "paid": "Pagamento simulado confirmado. +500 créditos.",
            "already_paid": "Esta cobrança já foi confirmada. Os créditos foram adicionados uma única vez.",
            "expired": "Esta cobrança expirou. Gere uma nova.",
        }
        for result, message in cases.items():
            self.confirm.return_value = result
            self.assertEqual(confirm_top_up(2, "ABC"), (result, message))
        self.confirm.assert_called_with(2, "ABC", "Recarga via PIX simulado · ABC")
        self.expire_overdue.assert_called_with(2)

    def test_confirm_top_up_unknown_charge(self):
        self.get_by_code.return_value = None
        self.assertEqual(confirm_top_up(2, "ABC"), ("not_found", ""))
        self.get_by_code.assert_called_once_with(2, "ABC")
        self.confirm.assert_not_called()


class StatementPageTest(unittest.TestCase):
    def test_parse_page_accepts_missing_and_positive_integers(self):
        for value, expected in [(None, 1), ("", 1), ("1", 1), ("7", 7)]:
            self.assertEqual(parse_page(value), (True, expected), value)

    def test_parse_page_rejects_everything_else(self):
        for value in ["abc", "0", "-1", "1.5", " 2", "1e3", "²", "9" * 5000]:
            self.assertEqual(parse_page(value), (False, None), value)

    def test_count_pages(self):
        self.assertEqual(count_pages(0, 20), 1)
        self.assertEqual(count_pages(20, 20), 1)
        self.assertEqual(count_pages(21, 20), 2)


if __name__ == "__main__":
    unittest.main()
