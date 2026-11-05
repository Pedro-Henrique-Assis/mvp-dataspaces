import unittest
from datetime import datetime
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


TRANSACTIONS = [
    {"created_at": datetime(2026, 11, 5, 10, 30), "description": "Requisição basic · API de entregas",
     "type": "request", "amount": -5, "balance_after": 115},
    {"created_at": datetime(2026, 11, 5, 9, 0), "description": "Recarga via PIX simulado",
     "type": "top_up", "amount": 500, "balance_after": 120},
    {"created_at": datetime(2026, 11, 4, 9, 0), "description": "Requisição de Fulana · API de entregas",
     "type": "earning", "amount": 5, "balance_after": 1005},
    {"created_at": datetime(2026, 11, 4, 8, 0), "description": "Saldo inicial",
     "type": "bonus", "amount": 120, "balance_after": 120},
    {"created_at": datetime(2026, 11, 3, 8, 0), "description": "Assinatura Plano simples · API de entregas",
     "type": "subscription", "amount": -100, "balance_after": 20},
]


class CreditsPageTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()
        with self.client.session_transaction() as session:
            session["organization_id"] = 2

    def page(self, transactions=TRANSACTIONS):
        with patch.object(credit_routes, "get_balance", return_value=120),                 patch.object(credit_routes, "list_for_organization", return_value=transactions) as listing,                 patch.object(credit_routes, "totals_for_organization", return_value={"spent": 105, "received": 5}) as totals:
            html = self.client.get("/credits").get_data(as_text=True)
        listing.assert_called_once_with(2)
        totals.assert_called_once_with(2)
        return html

    def test_shows_balance_and_totals(self):
        html = self.page()
        for text in ["Saldo atual: 120 créditos", "Total gasto: 105 créditos", "Total recebido: 5 créditos"]:
            self.assertIn(text, html)

    def test_shows_packages_with_usd_price_and_top_up_link(self):
        html = self.page()
        for credits_, price in [(500, "US$ 50.00"), (1000, "US$ 100.00"), (2500, "US$ 250.00")]:
            self.assertIn(f"{credits_} créditos", html)
            self.assertIn(price, html)
            self.assertIn(f"/credits/top-ups/new?package={credits_}", html)

    def test_statement_translates_types_and_shows_signed_values(self):
        html = self.page()
        for text in ["Bônus", "Recarga", "Assinatura", "Requisição", "Recebimento",
                     "+500", "-5", "-100", "+120", "2026-11-05 10:30", "Recarga via PIX simulado"]:
            self.assertIn(text, html)

    def test_statement_marks_entries_and_exits(self):
        html = self.page()
        self.assertEqual(html.count('class="credit-in"'), 3)
        self.assertEqual(html.count('class="credit-out"'), 2)

    def test_empty_statement(self):
        self.assertIn("Nenhuma movimentação", self.page([]))


if __name__ == "__main__":
    unittest.main()
