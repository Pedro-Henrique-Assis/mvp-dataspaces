import unittest

from app import create_app


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

    def test_login_page_links_to_registration(self):
        html = self.client.get("/login").get_data(as_text=True)
        self.assertIn("Registre-se", html)
        self.assertIn('href="/organizations/new"', html)


if __name__ == "__main__":
    unittest.main()
