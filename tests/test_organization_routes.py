import unittest
from datetime import date

from unittest.mock import patch

from app import create_app, credit_routes, organization_routes


class RegistrationFormTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()

    def test_form_is_public_and_has_fields(self):
        response = self.client.get("/organizations/new")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        for field in ["name", "cnpj", "email", "password", "password_confirmation",
                      "sector", "role", "contact_name", "description", "website", "accepted_terms"]:
            self.assertIn(f'name="{field}"', html)
        for role in ["consumer", "provider", "both"]:
            self.assertIn(f'value="{role}"', html)

    def test_form_has_api_block_that_can_be_hidden(self):
        html = self.client.get("/organizations/new").get_data(as_text=True)
        self.assertIn('id="api-fields"', html)
        for field in ["api_name", "api_description", "basic_response", "premium_response",
                      "policy_purpose", "policy_allows_redistribution", "policy_retention_days", "policy_notes"]:
            self.assertIn(f'name="{field}"', html)

    def test_terms_link_opens_pdf_in_new_tab(self):
        html = self.client.get("/organizations/new").get_data(as_text=True)
        self.assertIn('<a href="/static/docs/termos-de-uso.pdf" target="_blank" rel="noopener">termos de uso do Data Space</a>', html)

    def test_submit_button_is_tied_to_terms_checkbox(self):
        html = self.client.get("/organizations/new").get_data(as_text=True)
        self.assertIn('id="accepted_terms"', html)
        self.assertIn('id="submit-registration"', html)
        self.assertIn("submitButton.disabled = !terms.checked", html)

    def test_login_page_links_to_registration(self):
        html = self.client.get("/login").get_data(as_text=True)
        self.assertIn("Registre-se", html)
        self.assertIn('href="/organizations/new"', html)


class RegistrationSubmitTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()

    def submit(self, result):
        with patch.object(organization_routes, "register_organization", return_value=result):
            return self.client.post(
                "/organizations", data={"name": "Rota Certa", "password": "segredo123", "role": "consumer"}
            )

    def test_success_redirects_to_login_with_message(self):
        response = self.submit((True, []))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/login"))
        with self.client.session_transaction() as session:
            self.assertEqual(session["_flashes"][0][1], "Cadastro enviado. Aguarde a aprovação do administrador.")

    def test_errors_render_form_with_400_and_keep_values(self):
        response = self.submit((False, ["CNPJ inválido."]))
        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn("CNPJ inválido.", html)
        self.assertIn('value="Rota Certa"', html)

    def test_password_is_not_sent_back(self):
        html = self.submit((False, ["Erro."])).get_data(as_text=True)
        self.assertNotIn("segredo123", html)


CATALOG_ITEM = {
    "id": 1,
    "name": "TransLog Brasil",
    "sector": "logistics",
    "role": "both",
    "description": "Operadora logística.",
    "api_count": 2,
}


class CatalogTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()

    def get(self, items):
        with patch.object(organization_routes, "list_catalog", return_value=items):
            return self.client.get("/organizations")

    def test_catalog_is_public_and_lists_active_organizations(self):
        response = self.get([CATALOG_ITEM])
        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        for text in ["TransLog Brasil", "Logística", "Operadora logística.", "/organizations/1"]:
            self.assertIn(text, html)

    def test_catalog_shows_role_and_api_count(self):
        html = self.get([CATALOG_ITEM]).get_data(as_text=True)
        self.assertIn("Consumidora e fornecedora", html)
        self.assertIn("2 APIs", html)

    def test_empty_catalog(self):
        self.assertIn("Nenhuma organização", self.get([]).get_data(as_text=True))

    def test_menu_has_catalog_link_for_visitor(self):
        html = self.get([]).get_data(as_text=True)
        self.assertIn('href="/organizations"', html)


ORGANIZATION = {
    "id": 1,
    "name": "TransLog Brasil",
    "sector": "logistics",
    "role": "both",
    "contact_name": "Equipe TransLog",
    "website": "https://translog.example",
    "did": "did:example:translog",
    "description": None,
    "status": "active",
}
CREDENTIAL = {"issued_at": date(2026, 1, 1), "expires_at": date(2030, 12, 31)}
API = {
    "id": 10,
    "name": "API de entregas",
    "description": "Acompanhamento de entregas.",
    "basic_response": '[{"tracking_code": "SEGREDO-001", "status": "ok"}]',
    "premium_response": '[{"tracking_code": "SEGREDO-001", "status": "ok", "route_distance_km": 98.5}]',
    "policy_purpose": "Acompanhamento logístico",
    "policy_allows_redistribution": 0,
    "policy_retention_days": 90,
    "policy_notes": "Sem repasse a terceiros.",
}
PLANS = [
    {"id": 1, "name": "Plano simples", "subscription_price_credits": 100, "request_price_credits": 5, "max_access_level": "basic"},
    {"id": 2, "name": "Plano premium", "subscription_price_credits": 250, "request_price_credits": 2, "max_access_level": "premium"},
]


class OrganizationDetailTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()

    def get(self, organization=ORGANIZATION, logged_in=None):
        if logged_in:
            with self.client.session_transaction() as session:
                session["organization_id"] = logged_in
        with patch.object(organization_routes, "get_organization", return_value=organization),                 patch.object(organization_routes, "get_credential", return_value=CREDENTIAL),                 patch.object(organization_routes, "list_apis_for_provider", return_value=[API]),                 patch.object(organization_routes, "list_plans", return_value=PLANS),                 patch.object(credit_routes, "get_balance", return_value=120):
            return self.client.get("/organizations/1")

    def test_shows_organization_data_and_credential_validity(self):
        html = self.get().get_data(as_text=True)
        for text in ["TransLog Brasil", "Equipe TransLog", "https://translog.example",
                     "did:example:translog", "2026-01-01", "2030-12-31"]:
            self.assertIn(text, html)

    def test_missing_or_inactive_organization_is_404(self):
        for organization in [None, dict(ORGANIZATION, status="pending"), dict(ORGANIZATION, status="rejected")]:
            self.assertEqual(self.get(organization).status_code, 404)

    def test_shows_plans_policy_and_fields_but_not_data(self):
        html = self.get().get_data(as_text=True)
        for text in ["API de entregas", "Plano simples", "Plano premium", "Acompanhamento logístico",
                     "90 dias", "Sem repasse a terceiros.", "tracking_code", "status", "route_distance_km"]:
            self.assertIn(text, html)
        self.assertNotIn("SEGREDO-001", html)

    def test_plan_prices_are_shown_in_credits(self):
        html = self.get().get_data(as_text=True)
        for text in ["100 créditos", "250 créditos", "5 créditos", "2 créditos"]:
            self.assertIn(text, html)
        self.assertNotIn("US$", html)

    def test_subscribe_button_depends_on_login(self):
        self.assertNotIn("/subscriptions?api_id=10", self.get().get_data(as_text=True))
        self.assertNotIn("/subscriptions?api_id=10", self.get(logged_in=1).get_data(as_text=True))
        self.assertIn("/subscriptions?api_id=10", self.get(logged_in=2).get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
