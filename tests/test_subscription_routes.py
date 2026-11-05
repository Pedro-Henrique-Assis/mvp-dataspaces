import unittest
from datetime import date
from unittest.mock import patch

from app import create_app, subscription_routes, usage_routes

CREDENTIAL = {
    "status": "active",
    "issuer_did": "did:example:dataspace-authority",
    "subject_did": "did:example:cargacerta",
    "role_provider": True,
    "role_consumer": True,
    "expires_at": date(2030, 12, 31),
}
ORGANIZATION = {"id": 2, "did": "did:example:cargacerta"}
APIS = [
    {"id": 1, "name": "API de entregas", "description": "Entregas.", "provider_name": "TransLog Brasil"},
    {"id": 3, "name": "API de rotas", "description": "Rotas.", "provider_name": "Rota Certa"},
]
PLANS = [
    {"id": 1, "name": "Plano simples", "subscription_price_credits": 100, "request_price_credits": 5}
]


class SubscriptionRoutesTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()
        with self.client.session_transaction() as session:
            session["organization_id"] = 2

    def get(self, url="/subscriptions", credential=CREDENTIAL):
        with patch.object(subscription_routes, "list_available_for", return_value=APIS) as listing, \
                patch.object(subscription_routes, "list_plans", return_value=PLANS), \
                patch.object(subscription_routes, "get_credential", return_value=credential), \
                patch.object(subscription_routes, "get_organization", return_value=ORGANIZATION):
            response = self.client.get(url)
        self.listing = listing
        return response

    def test_lists_apis_available_to_the_consumer(self):
        html = self.get().get_data(as_text=True)
        self.listing.assert_called_once_with(2)
        self.assertIn("API de entregas", html)
        self.assertIn("API de rotas", html)

    def test_api_id_preselects_that_api(self):
        html = self.get("/subscriptions?api_id=3").get_data(as_text=True)
        self.assertLess(html.index("API de rotas"), html.index("API de entregas"))
        self.assertIn("Selecionada", html)

    def test_plan_option_shows_credit_prices(self):
        html = self.get().get_data(as_text=True)
        self.assertIn("Plano simples — 100 créditos + 5 por requisição", html)

    def test_without_api_id_nothing_is_marked(self):
        self.assertNotIn("Selecionada", self.get().get_data(as_text=True))

    def test_organization_without_consumer_role_sees_message_and_no_form(self):
        provider_only = dict(CREDENTIAL, role_consumer=False)
        html = self.get(credential=provider_only).get_data(as_text=True)
        self.assertIn("A organização não está habilitada como consumidora.", html)
        self.assertNotIn("<select", html)

    def test_post_creates_subscription(self):
        with patch.object(subscription_routes, "create_subscription", return_value=(True, 7)) as create:
            response = self.client.post("/subscriptions", data={"api_id": 3, "plan_id": 1})
        self.assertEqual(create.call_args.args[:3], (2, 3, 1))
        self.assertTrue(response.headers["Location"].endswith("/dashboard"))

    def test_post_without_plan_goes_back_with_error(self):
        response = self.client.post("/subscriptions", data={"api_id": 3})
        self.assertTrue(response.headers["Location"].endswith("/subscriptions"))
        with self.client.session_transaction() as session:
            self.assertEqual(session["_flashes"][0], ("error", "Selecione uma API e um plano."))

    def test_old_create_route_is_gone(self):
        self.assertEqual(self.client.post("/subscriptions/create", data={"api_id": 3, "plan_id": 1}).status_code, 404)

    def test_usage_has_no_trailing_slash_redirect(self):
        with patch.object(usage_routes, "summary_for_consumer", return_value=[]):
            self.assertEqual(self.client.get("/usage").status_code, 200)


if __name__ == "__main__":
    unittest.main()
