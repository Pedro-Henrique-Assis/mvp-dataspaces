import unittest
from unittest.mock import patch

from app import create_app, usage_routes

ITEM = {
    "api_name": "API de entregas",
    "plan_name": "Plano simples",
    "request_count": 4,
    "subscription_price_credits": 100,
    "request_total": 20,
}


class UsageRoutesTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()
        with self.client.session_transaction() as session:
            session["organization_id"] = 2

    def test_usage_shows_subscription_requests_and_total_in_credits(self):
        with patch.object(usage_routes, "summary_for_consumer", return_value=[ITEM]):
            html = self.client.get("/usage").get_data(as_text=True)
        for text in ["API de entregas", "Plano simples", "100 créditos", "20 créditos", "120 créditos"]:
            self.assertIn(text, html)
        self.assertNotIn("US$", html)


if __name__ == "__main__":
    unittest.main()
