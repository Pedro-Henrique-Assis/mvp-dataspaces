import unittest

from app.services.registration_service import is_valid_cnpj, only_digits


class CnpjTest(unittest.TestCase):
    def test_only_digits_removes_mask(self):
        self.assertEqual(only_digits("11.222.333/0001-81"), "11222333000181")

    def test_valid_cnpj(self):
        self.assertTrue(is_valid_cnpj("11222333000181"))
        self.assertTrue(is_valid_cnpj("44555666000181"))

    def test_valid_cnpj_with_mask(self):
        self.assertTrue(is_valid_cnpj("11.222.333/0001-81"))

    def test_wrong_check_digits(self):
        self.assertFalse(is_valid_cnpj("11222333000182"))
        self.assertFalse(is_valid_cnpj("11222333000191"))

    def test_repeated_digits(self):
        self.assertFalse(is_valid_cnpj("00000000000000"))
        self.assertFalse(is_valid_cnpj("11111111111111"))

    def test_wrong_length(self):
        self.assertFalse(is_valid_cnpj("1122233300018"))
        self.assertFalse(is_valid_cnpj("112223330001811"))
        self.assertFalse(is_valid_cnpj(""))


if __name__ == "__main__":
    unittest.main()
