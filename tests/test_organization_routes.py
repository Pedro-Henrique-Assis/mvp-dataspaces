import unittest

from unittest.mock import patch

from app import create_app, organization_routes


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


if __name__ == "__main__":
    unittest.main()
