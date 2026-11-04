import html
import unittest
from unittest.mock import patch

from app import admin_routes, create_app

PENDING = {
    "id": 5,
    "name": "Rota Certa Ltda",
    "cnpj": "12345678000195",
    "email": "contato@rotacerta.com.br",
    "sector": "transport",
    "role": "provider",
    "contact_name": "Maria",
    "description": None,
    "website": None,
    "status": "pending",
    "rejection_reason": None,
    "created_at": None,
    "apis": [
        {
            "name": "API de Rotas",
            "description": "Rotas.",
            "basic_response": '[{"cidade":"São Paulo","id":1}]',
            "premium_response": '[{"cidade":"São Paulo","id":1,"km":10}]',
            "policy_purpose": "Planejamento",
            "policy_allows_redistribution": 0,
            "policy_retention_days": 30,
            "policy_notes": None,
        }
    ],
}


class AdminQueueTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()
        with self.client.session_transaction() as session:
            session["admin_id"] = 1
        patcher = patch.object(admin_routes, "count_by_status", return_value=1)
        patcher.start()
        self.addCleanup(patcher.stop)

    def get(self, url, orgs=(PENDING,)):
        with patch.object(admin_routes, "list_by_status", return_value=list(orgs)) as listing:
            return self.client.get(url), listing

    def test_default_status_is_pending(self):
        response, listing = self.get("/admin/organizations")
        self.assertEqual(response.status_code, 200)
        listing.assert_called_once_with("pending")
        self.assertIn("Rota Certa Ltda", response.get_data(as_text=True))

    def test_status_filter(self):
        _, listing = self.get("/admin/organizations?status=rejected")
        listing.assert_called_once_with("rejected")

    def test_unknown_status_falls_back_to_pending(self):
        _, listing = self.get("/admin/organizations?status=banana")
        listing.assert_called_once_with("pending")

    def test_api_json_is_shown_formatted_with_accents(self):
        page = self.get("/admin/organizations")[0].get_data(as_text=True)
        self.assertIn("<pre>", page)
        self.assertIn('"cidade": "São Paulo"', html.unescape(page))
        self.assertIn("API de Rotas", page)
        self.assertIn("Planejamento", page)

    def test_empty_queue_message(self):
        html = self.get("/admin/organizations", orgs=())[0].get_data(as_text=True)
        self.assertIn("Nenhum cadastro", html)


class AdminDecisionTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()

    def login_admin(self):
        with self.client.session_transaction() as session:
            session["admin_id"] = 1

    def flashes(self):
        with self.client.session_transaction() as session:
            return session["_flashes"]

    def test_approval_requires_admin(self):
        response = self.client.post("/admin/organizations/5/approval")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/login"))

    def test_approval_is_post_only(self):
        self.login_admin()
        self.assertEqual(self.client.get("/admin/organizations/5/approval").status_code, 405)

    def test_approve_flashes_success_and_returns_to_queue(self):
        self.login_admin()
        with patch.object(admin_routes, "approve_organization", return_value=(True, "ok")) as approve:
            response = self.client.post("/admin/organizations/5/approval")
        self.assertEqual(approve.call_args.args[0], 5)
        self.assertTrue(response.headers["Location"].endswith("/admin/organizations"))
        self.assertEqual(self.flashes()[0][0], "success")

    def test_failed_approval_flashes_error(self):
        self.login_admin()
        message = "Somente cadastros pendentes podem ser aprovados."
        with patch.object(admin_routes, "approve_organization", return_value=(False, message)):
            self.client.post("/admin/organizations/5/approval")
        self.assertEqual(self.flashes()[0], ("error", message))

    def test_reject_sends_reason_and_returns_to_queue(self):
        self.login_admin()
        with patch.object(admin_routes, "reject_organization", return_value=(True, "Cadastro rejeitado.")) as reject:
            response = self.client.post("/admin/organizations/5/rejection", data={"reason": "CNPJ divergente"})
        reject.assert_called_once_with(5, "CNPJ divergente")
        self.assertTrue(response.headers["Location"].endswith("/admin/organizations"))
        self.assertEqual(self.flashes()[0][0], "success")

    def test_failed_rejection_flashes_error(self):
        self.login_admin()
        with patch.object(admin_routes, "reject_organization", return_value=(False, "Informe o motivo da rejeição.")):
            self.client.post("/admin/organizations/5/rejection", data={})
        self.assertEqual(self.flashes()[0], ("error", "Informe o motivo da rejeição."))

    def test_rejection_requires_admin(self):
        self.assertEqual(self.client.post("/admin/organizations/5/rejection").status_code, 302)

    def test_queue_shows_decision_forms_only_for_pending(self):
        self.login_admin()
        with patch.object(admin_routes, "count_by_status", return_value=1),                 patch.object(admin_routes, "list_by_status", return_value=[PENDING]):
            page = self.client.get("/admin/organizations").get_data(as_text=True)
        self.assertIn("/admin/organizations/5/approval", page)
        self.assertIn("/admin/organizations/5/rejection", page)
        self.assertIn('name="reason"', page)
        with patch.object(admin_routes, "count_by_status", return_value=0),                 patch.object(admin_routes, "list_by_status", return_value=[dict(PENDING, status="active")]):
            page = self.client.get("/admin/organizations?status=active").get_data(as_text=True)
        self.assertNotIn("/approval", page)


if __name__ == "__main__":
    unittest.main()
