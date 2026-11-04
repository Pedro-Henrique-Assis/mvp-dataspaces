import unittest
from datetime import date
from unittest.mock import patch

from app import create_app, routes


class DashboardTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()
        with self.client.session_transaction() as session:
            session["organization_id"] = 1

    def get(self, credential):
        with patch.object(routes, "list_public", return_value=[]), \
                patch.object(routes, "list_for_consumer", return_value=[]), \
                patch.object(routes, "get_credential", return_value=credential) as get_credential:
            response = self.client.get("/dashboard")
        get_credential.assert_called_once_with(1)
        return response.get_data(as_text=True)

    def test_shows_credential_validity(self):
        html = self.get({"issued_at": date(2026, 11, 4), "expires_at": date(2027, 11, 4)})
        self.assertIn("2026-11-04", html)
        self.assertIn("2027-11-04", html)

    def test_dashboard_works_without_credential(self):
        self.assertIn("Dashboard", self.get(None))


if __name__ == "__main__":
    unittest.main()
