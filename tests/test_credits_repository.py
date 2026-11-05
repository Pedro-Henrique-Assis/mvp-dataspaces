import unittest

from app.repositories import credits


class FakeCursor:
    def __init__(self, rowcount=1, balance=150):
        self.rowcount = rowcount
        self.balance = balance
        self.executed = []

    def execute(self, sql, params=()):
        self.executed.append((sql, params))

    def fetchone(self):
        return (self.balance,)


class DebitTest(unittest.TestCase):
    def test_debit_succeeds_when_one_row_is_updated(self):
        cursor = FakeCursor(rowcount=1)
        self.assertTrue(credits.debit(cursor, 7, 40))
        sql, params = cursor.executed[0]
        self.assertIn("credit_balance >= %s", sql)
        self.assertEqual(params, (40, 7, 40))

    def test_debit_fails_when_balance_is_not_enough(self):
        self.assertFalse(credits.debit(FakeCursor(rowcount=0), 7, 40))


class CreditTest(unittest.TestCase):
    def test_credit_adds_to_balance(self):
        cursor = FakeCursor()
        credits.credit(cursor, 7, 40)
        sql, params = cursor.executed[0]
        self.assertIn("credit_balance = credit_balance + %s", sql)
        self.assertEqual(params, (40, 7))


class LogTest(unittest.TestCase):
    def test_log_stores_balance_read_from_database(self):
        cursor = FakeCursor(balance=150)
        credits.log(cursor, 7, -40, "request", "Requisição basic · API de entregas")
        self.assertIn("SELECT credit_balance", cursor.executed[0][0])
        sql, params = cursor.executed[1]
        self.assertIn("INSERT INTO credit_transactions", sql)
        self.assertEqual(params, (7, -40, "request", "Requisição basic · API de entregas", 150))


if __name__ == "__main__":
    unittest.main()
