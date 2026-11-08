import unittest

from app import create_app


class TermsTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()

    def test_terms_page_is_public(self):
        response = self.client.get("/terms")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Termos de uso do Data Space", html)
        self.assertIn("Créditos e cobrança", html)
        self.assertIn('href="/static/docs/termos-de-uso.pdf"', html)

    def test_pdf_is_served(self):
        response = self.client.get("/static/docs/termos-de-uso.pdf")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/pdf")
        self.assertTrue(response.data.startswith(b"%PDF"))
        response.close()

    def test_footer_links_to_terms(self):
        html = self.client.get("/terms").get_data(as_text=True)
        self.assertIn('href="/terms"', html)


if __name__ == "__main__":
    unittest.main()
