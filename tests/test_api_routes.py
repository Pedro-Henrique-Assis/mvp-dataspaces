import json
import unittest
from datetime import date
from unittest.mock import patch

from app import api_routes, create_app

CREDENTIAL = {
    "status": "active",
    "issuer_did": "did:example:dataspace-authority",
    "subject_did": "did:example:translog",
    "role_provider": True,
    "role_consumer": True,
    "expires_at": date(2030, 12, 31),
}
ORGANIZATION = {"id": 1, "did": "did:example:translog", "status": "active"}
API = {
    "id": 2,
    "name": "API de veículos",
    "provider_name": "CargaCerta Transportes",
    "provider_status": "active",
    "basic_response": json.dumps([{"vehicle_code": "VEI-001"}]),
    "premium_response": json.dumps([{"vehicle_code": "VEI-001", "capacity_kg": 12000}]),
}
SIMPLE = {
    "id": 5,
    "status": "active",
    "max_access_level": "basic",
    "request_price_usd": "0.50",
    "subscription_price_usd": "10.00",
}
PREMIUM = dict(SIMPLE, max_access_level="premium")
URL = "/api/v1/apis/veiculos/data"


class ApiRoutesTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()

    def login(self):
        with self.client.session_transaction() as session:
            session["organization_id"] = 1

    def request(self, path=URL, api=API, credential=CREDENTIAL, subscription=SIMPLE):
        self.login()
        patchers = (
            patch.object(api_routes, "get_by_slug", return_value=api),
            patch.object(api_routes, "get_for_organization", return_value=credential),
            patch.object(api_routes, "get_organization", return_value=ORGANIZATION),
            patch.object(api_routes, "find_active", return_value=subscription),
            patch.object(api_routes, "register_request"),
        )
        mocks = [p.start() for p in patchers]
        self.addCleanup(lambda: [p.stop() for p in patchers])
        return self.client.get(path), mocks[-1]

    def test_requires_login_with_json_error(self):
        response = self.client.get(URL)
        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.json)

    def test_basic_is_default_level_and_registers_request(self):
        response, register = self.request()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json,
            {
                "api": "API de veículos",
                "provider": "CargaCerta Transportes",
                "access_level": "basic",
                "data": [{"vehicle_code": "VEI-001"}],
            },
        )
        register.assert_called_once()

    def test_premium_with_premium_plan_returns_premium_response(self):
        response, _ = self.request(URL + "?level=premium", subscription=PREMIUM)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["data"][0]["capacity_kg"], 12000)

    def test_premium_blocked_without_charge(self):
        response, register = self.request(URL + "?level=premium")
        self.assertEqual(response.status_code, 403)
        register.assert_not_called()

    def test_invalid_level(self):
        response, _ = self.request(URL + "?level=gold")
        self.assertEqual(response.status_code, 400)

    def test_unknown_api(self):
        response, _ = self.request(api=None)
        self.assertEqual(response.status_code, 404)

    def test_inactive_provider_is_not_found(self):
        response, register = self.request(api=dict(API, provider_status="pending"))
        self.assertEqual(response.status_code, 404)
        register.assert_not_called()

    def test_expired_credential_blocks_access(self):
        expired = dict(CREDENTIAL, expires_at=date(2020, 1, 1))
        response, register = self.request(credential=expired)
        self.assertEqual(response.status_code, 403)
        register.assert_not_called()

    def test_organization_without_consumer_role_is_forbidden(self):
        provider_only = dict(CREDENTIAL, role_consumer=False)
        response, register = self.request(credential=provider_only)
        self.assertEqual(response.status_code, 403)
        register.assert_not_called()

    def test_without_subscription_is_forbidden(self):
        response, register = self.request(subscription=None)
        self.assertEqual(response.status_code, 403)
        register.assert_not_called()

    def test_old_routes_are_gone(self):
        self.login()
        self.assertEqual(self.client.get("/api/veiculos/basic").status_code, 404)


if __name__ == "__main__":
    unittest.main()
