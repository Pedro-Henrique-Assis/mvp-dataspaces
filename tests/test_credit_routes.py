import unittest
from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

from app import create_app, credit_routes, routes, subscription_routes
from app.services import credit_service


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
        with patch.object(credit_routes, "get_balance", return_value=120),                 patch.object(credit_routes, "expire_overdue"),                 patch.object(credit_routes, "list_for_organization", return_value=transactions) as listing,                 patch.object(credit_routes, "totals_for_organization", return_value={"spent": 105, "received": 5}) as totals:
            html = self.client.get("/credits").get_data(as_text=True)
        listing.assert_called_once_with(2)
        totals.assert_called_once_with(2)
        return html

    def test_shows_balance_and_totals(self):
        html = self.page()
        for text in ["Saldo atual: 120 créditos", "Total gasto: 105 créditos", "Total recebido: 5 créditos"]:
            self.assertIn(text, html)

    def test_packages_are_post_forms(self):
        html = self.page()
        self.assertIn('<form method="post" action="/credits/top-ups">', html)
        self.assertIn('name="package" value="500"', html)

    def test_shows_packages_with_usd_price(self):
        html = self.page()
        for credits_, price in [(500, "US$ 50.00"), (1000, "US$ 100.00"), (2500, "US$ 250.00")]:
            self.assertIn(f"{credits_} créditos", html)
            self.assertIn(price, html)

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


class TopUpTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()
        balance = patch.object(credit_routes, "get_balance", return_value=120)
        balance.start()
        self.addCleanup(balance.stop)

    def login(self):
        with self.client.session_transaction() as session:
            session["organization_id"] = 2

    def flashes(self):
        with self.client.session_transaction() as session:
            return session["_flashes"]

    def charge(self, **changes):
        data = {"code": "ABC", "credits": 500, "amount_usd": Decimal("50.00"), "status": "pending",
                "expires_at": datetime(2026, 11, 5, 14, 35), "paid_at": None}
        data.update(changes)
        return data

    def show(self, charge):
        self.login()
        with patch.object(credit_routes, "expire_overdue"),                 patch.object(credit_routes, "get_by_code", return_value=charge):
            return self.client.get("/credits/top-ups/ABC")

    def test_post_top_up_redirects_to_charge(self):
        self.login()
        with patch.object(credit_routes, "open_top_up", return_value=(True, "ABC")):
            response = self.client.post("/credits/top-ups", data={"package": "500"})
        self.assertTrue(response.headers["Location"].endswith("/credits/top-ups/ABC"))

    def test_post_top_up_with_invalid_package(self):
        self.login()
        for data in [{"package": "999999"}, {}]:
            with patch.object(credit_routes, "open_top_up", return_value=(False, "Pacote de créditos inválido.")):
                response = self.client.post("/credits/top-ups", data=data)
            self.assertTrue(response.headers["Location"].endswith("/credits"))
            self.assertEqual(self.flashes()[-1], ("error", "Pacote de créditos inválido."))

    def test_pending_charge_page(self):
        html = self.show(self.charge()).get_data(as_text=True)
        for text in ["US$ 50.00", "ABC", "Válida até 14:35", "Confirmar pagamento simulado",
                     'action="/credits/top-ups/ABC/confirmation"']:
            self.assertIn(text, html)

    def test_paid_charge_page(self):
        html = self.show(self.charge(status="paid", paid_at=datetime(2026, 11, 5, 14, 30))).get_data(as_text=True)
        self.assertIn("Pagamento confirmado em 05/11/2026 14:30.", html)
        self.assertNotIn("Confirmar pagamento simulado", html)

    def test_expired_charge_page_offers_new_charge(self):
        html = self.show(self.charge(status="expired")).get_data(as_text=True)
        for text in ["Cobrança expirada.", "Gerar nova cobrança", 'name="package" value="500"']:
            self.assertIn(text, html)

    def test_unknown_charge_is_404(self):
        self.assertEqual(self.show(None).status_code, 404)

    def confirm(self, result, message=""):
        self.login()
        with patch.object(credit_routes, "confirm_top_up", return_value=(result, message)) as confirm_top_up:
            response = self.client.post("/credits/top-ups/ABC/confirmation")
        confirm_top_up.assert_called_once_with(2, "ABC")
        return response

    def test_confirm_paid_redirects_to_credits(self):
        response = self.confirm("paid", "Pagamento simulado confirmado. +500 créditos.")
        self.assertTrue(response.headers["Location"].endswith("/credits"))
        self.assertEqual(self.flashes()[-1], ("success", "Pagamento simulado confirmado. +500 créditos."))

    def test_confirm_already_paid_redirects_to_credits_with_error(self):
        response = self.confirm("already_paid", "Esta cobrança já foi confirmada.")
        self.assertTrue(response.headers["Location"].endswith("/credits"))
        self.assertEqual(self.flashes()[-1], ("error", "Esta cobrança já foi confirmada."))

    def test_confirm_expired_redirects_to_charge(self):
        response = self.confirm("expired", "Esta cobrança expirou. Gere uma nova.")
        self.assertTrue(response.headers["Location"].endswith("/credits/top-ups/ABC"))
        self.assertEqual(self.flashes()[-1], ("error", "Esta cobrança expirou. Gere uma nova."))

    def test_confirm_not_found_is_404(self):
        self.assertEqual(self.confirm("not_found").status_code, 404)

    def test_confirm_charge_of_other_organization_is_404(self):
        with self.client.session_transaction() as session:
            session["organization_id"] = 3
        with patch.object(credit_service, "expire_overdue"),                 patch.object(credit_service, "get_by_code", return_value=None) as get_by_code,                 patch.object(credit_service, "confirm", return_value="not_found") as confirm:
            response = self.client.post("/credits/top-ups/ABC/confirmation")
        self.assertEqual(response.status_code, 404)
        get_by_code.assert_called_once_with(3, "ABC")
        confirm.assert_not_called()

    def test_old_new_route_is_gone(self):
        self.login()
        with patch.object(credit_routes, "expire_overdue"),                 patch.object(credit_routes, "get_by_code", return_value=None):
            response = self.client.get("/credits/top-ups/new?package=500")
        self.assertEqual(response.status_code, 404)

    def test_routes_require_login(self):
        post = self.client.post("/credits/top-ups", data={"package": "500"})
        get = self.client.get("/credits/top-ups/ABC")
        confirm = self.client.post("/credits/top-ups/ABC/confirmation")
        for response in (post, get, confirm):
            self.assertTrue(response.headers["Location"].endswith("/login"))

    def test_create_is_post_only(self):
        self.login()
        self.assertEqual(self.client.get("/credits/top-ups").status_code, 405)


if __name__ == "__main__":
    unittest.main()
