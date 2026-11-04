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
ORGANIZATION = {"id": 1, "did": "did:example:translog", "active": True}
API = {"id": 2, "name": "API de veículos"}
SIMPLE = {
    "id": 5,
    "status": "active",
    "max_access_level": "basic",
    "request_price_usd": "0.50",
    "subscription_price_usd": "10.00",
}


class ApiRoutesTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()

    def login(self):
        with self.client.session_transaction() as session:
            session["organization_id"] = 1

    def patches(self, credential=CREDENTIAL, subscription=SIMPLE):
        return (
            patch.object(api_routes, "get_by_slug", return_value=API),
            patch.object(api_routes, "get_for_organization", return_value=credential),
            patch.object(api_routes, "get_organization", return_value=ORGANIZATION),
            patch.object(api_routes, "find_active", return_value=subscription),
            patch.object(api_routes, "list_vehicles", return_value=[{"vehicle_code": "VEI-001"}]),
            patch.object(api_routes, "register_request"),
        )

    def request(self, path, **kwargs):
        self.login()
        patchers = self.patches(**kwargs)
        mocks = [p.start() for p in patchers]
        self.addCleanup(lambda: [p.stop() for p in patchers])
        return self.client.get(path), mocks[-1]

    def test_requires_login_with_json_error(self):
        response = self.client.get("/api/veiculos/basic")
        self.assertEqual(response.status_code, 401)

    def test_basic_access_registers_request(self):
        response, register = self.request("/api/veiculos/basic")
        self.assertEqual(response.status_code, 200)
        register.assert_called_once()

    def test_premium_blocked_without_charge(self):
        response, register = self.request("/api/veiculos/premium")
        self.assertEqual(response.status_code, 403)
        register.assert_not_called()

    def test_invalid_level(self):
        response, _ = self.request("/api/veiculos/gold")
        self.assertEqual(response.status_code, 400)

    def test_expired_credential_blocks_access(self):
        expired = dict(CREDENTIAL, expires_at=date(2020, 1, 1))
        response, register = self.request("/api/veiculos/basic", credential=expired)
        self.assertEqual(response.status_code, 403)
        register.assert_not_called()


if __name__ == "__main__":
    unittest.main()
