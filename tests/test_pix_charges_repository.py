import unittest
from unittest.mock import patch

from app.repositories import pix_charges


class FakeCursor:
    def __init__(self, rowcount, rows):
        self.rowcount = rowcount
        self.rows = list(rows)
        self.calls = []

    def execute(self, sql, params=None):
        self.calls.append(sql)

    def fetchone(self):
        return self.rows.pop(0) if self.rows else None

    def close(self):
        pass


class FakeConnection:
    def __init__(self, cursor):
        self._cursor = cursor
        self.committed = False
        self.rolled_back = False

    def cursor(self, dictionary=False):
        return self._cursor

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        pass


def run_confirm(rowcount, rows):
    cursor = FakeCursor(rowcount, rows)
    connection = FakeConnection(cursor)
    with patch.object(pix_charges, "get_connection", return_value=connection), \
            patch.object(pix_charges, "credits") as credits_mock:
        result = pix_charges.confirm(2, "CODE", "Recarga via PIX simulado · X")
    return result, cursor, connection, credits_mock


class ConfirmTest(unittest.TestCase):
    def test_confirm_pending_charge_credits_once(self):
        result, cursor, connection, credits_mock = run_confirm(1, [(500,)])
        self.assertEqual(result, "paid")
        credits_mock.credit.assert_called_once_with(cursor, 2, 500)
        credits_mock.log.assert_called_once_with(
            cursor, 2, 500, "top_up", "Recarga via PIX simulado · X"
        )
        self.assertTrue(connection.committed)

    def test_confirm_paid_charge_does_not_credit(self):
        result, _, _, credits_mock = run_confirm(0, [("paid",)])
        self.assertEqual(result, "already_paid")
        credits_mock.credit.assert_not_called()

    def test_confirm_unknown_charge(self):
        result, _, _, _ = run_confirm(0, [])
        self.assertEqual(result, "not_found")

    def test_confirm_overdue_charge_is_marked_expired(self):
        result, cursor, connection, credits_mock = run_confirm(0, [("pending",)])
        self.assertEqual(result, "expired")
        self.assertTrue(any("SET status = 'expired'" in sql for sql in cursor.calls))
        credits_mock.credit.assert_not_called()
        self.assertTrue(connection.committed)

    def test_confirm_only_updates_pending_and_valid_charge(self):
        _, cursor, _, _ = run_confirm(0, [("paid",)])
        self.assertIn("status = 'pending'", cursor.calls[0])
        self.assertIn("expires_at >= NOW()", cursor.calls[0])


class FindOpenTest(unittest.TestCase):
    def test_find_open_requires_valid_charge_of_same_package(self):
        cursor = FakeCursor(0, [("CODE",)])
        connection = FakeConnection(cursor)
        with patch.object(pix_charges, "get_connection", return_value=connection):
            code = pix_charges.find_open(2, 500)
        self.assertEqual(code, "CODE")
        sql = cursor.calls[0]
        self.assertIn("credits = %s", sql)
        self.assertIn("status = 'pending'", sql)
        self.assertIn("expires_at >= NOW()", sql)


if __name__ == "__main__":
    unittest.main()
