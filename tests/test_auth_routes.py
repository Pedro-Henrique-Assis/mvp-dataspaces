import unittest
from unittest.mock import patch

from app import auth_routes, create_app


class AuthRoutesTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()

    def post_login(self, result):
        with patch.object(auth_routes, "authenticate", return_value=result) as authenticate:
            response = self.client.post("/login", data={"email": "a@b.com", "password": "x"})
        return response, authenticate

    def test_login_page_has_email_and_password(self):
        html = self.client.get("/login").get_data(as_text=True)
        self.assertIn('name="email"', html)
        self.assertIn('name="password"', html)

    def test_organization_goes_to_dashboard(self):
        response, authenticate = self.post_login(("organization", {"id": 3, "name": "Org"}, None))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/dashboard"))
        authenticate.assert_called_once()
        with self.client.session_transaction() as session:
            self.assertEqual(session["organization_id"], 3)

    def test_admin_session_uses_admin_id(self):
        response, _ = self.post_login(("admin", {"id": 1, "name": "Admin"}, None))
        self.assertTrue(response.headers["Location"].endswith("/admin/organizations"))
        with self.client.session_transaction() as session:
            self.assertEqual(session["admin_id"], 1)
            self.assertNotIn("organization_id", session)

    def test_invalid_login_shows_message_without_session(self):
        response, _ = self.post_login((None, None, "E-mail ou senha inválidos."))
        self.assertEqual(response.status_code, 200)
        self.assertIn("E-mail ou senha inválidos.", response.get_data(as_text=True))
        with self.client.session_transaction() as session:
            self.assertNotIn("organization_id", session)


if __name__ == "__main__":
    unittest.main()
