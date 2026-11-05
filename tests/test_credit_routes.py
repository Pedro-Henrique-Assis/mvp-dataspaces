import unittest
from unittest.mock import patch

from app import create_app, credit_routes, routes, subscription_routes


class CreditMenuTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()
        patcher = patch.object(credit_routes, "get_balance", return_value=120)
        self.get_balance = patcher.start()
        self.addCleanup(patcher.stop)
        for name in ["list_public"]:
            other = patch.object(routes, name, return_value=[])
            other.start()
            self.addCleanup(other.stop)

    def login(self, key="organization_id"):
        with self.client.session_transaction() as session:
            session[key] = 2

    def test_organization_menu_shows_balance_linking_to_credits(self):
        self.login()
        html = self.client.get("/").get_data(as_text=True)
        self.assertIn("Créditos: 120", html)
        self.assertIn('href="/credits"', html)
        self.get_balance.assert_called_with(2)

    def test_visitor_does_not_query_the_balance(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertNotIn("Créditos:", html)
        self.get_balance.assert_not_called()

    def test_admin_does_not_query_the_balance(self):
        self.login("admin_id")
        with patch.object(routes, "list_public", return_value=[]), \
                patch("app.admin_routes.count_by_status", return_value=0):
            html = self.client.get("/").get_data(as_text=True)
        self.assertNotIn("Créditos:", html)
        self.get_balance.assert_not_called()

    def test_credits_page_requires_login(self):
        response = self.client.get("/credits")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/login"))

    def test_admin_is_redirected_from_credits_page(self):
        self.login("admin_id")
        response = self.client.get("/credits")
        self.assertTrue(response.headers["Location"].endswith("/admin/organizations"))

    def test_subscriptions_page_shows_balance(self):
        self.login()
        with patch.object(subscription_routes, "list_available_for", return_value=[]), \
                patch.object(subscription_routes, "list_plans", return_value=[]), \
                patch.object(subscription_routes, "get_credential", return_value=None), \
                patch.object(subscription_routes, "get_organization", return_value=None):
            html = self.client.get("/subscriptions").get_data(as_text=True)
        self.assertIn("Saldo: 120 créditos", html)


if __name__ == "__main__":
    unittest.main()
