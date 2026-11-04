import unittest
from unittest.mock import patch

from app import admin_routes, create_app, routes


class AdminAccessTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()
        for target, name, value in [(admin_routes, "count_by_status", 4), (routes, "list_public", [])]:
            patcher = patch.object(target, name, return_value=value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def login(self, key, value=1):
        with self.client.session_transaction() as session:
            session[key] = value

    def test_visitor_is_sent_to_login(self):
        response = self.client.get("/admin/organizations")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/login"))

    def test_organization_gets_403(self):
        self.login("organization_id")
        self.assertEqual(self.client.get("/admin/organizations").status_code, 403)

    def test_admin_sees_queue_with_pending_count(self):
        self.login("admin_id")
        response = self.client.get("/admin/organizations")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Aprovações (4 pendentes)", response.get_data(as_text=True))

    def test_admin_is_redirected_from_organization_pages(self):
        self.login("admin_id")
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.headers["Location"].endswith("/admin/organizations"))
        with self.client.session_transaction() as session:
            flashes = session["_flashes"]
        self.assertEqual(flashes[0][1], "Esta página é exclusiva para organizações.")

    def test_visitor_menu_has_login_only(self):
        html = self.client.get("/").get_data(as_text=True)
        self.assertNotIn("Aprovações", html)
        self.assertIn("Entrar", html)


if __name__ == "__main__":
    unittest.main()
