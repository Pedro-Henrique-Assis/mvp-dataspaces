import unittest
from datetime import date
from unittest.mock import patch

from app.services import subscription_service as service

ISSUER = "did:example:dataspace-authority"
CONSUMER = {"id": 2, "did": "did:example:cargacerta"}
CREDENTIAL = {
    "status": "active",
    "issuer_did": ISSUER,
    "subject_did": "did:example:cargacerta",
    "role_provider": True,
    "role_consumer": True,
    "expires_at": date(2030, 12, 31),
}

PROVIDER_API = {"id": 1, "provider_org_id": 1, "provider_status": "active"}


def run(api, plan, existing=None, credential=CREDENTIAL):
    with patch.object(service, "get_organization", return_value=CONSUMER), \
         patch.object(service, "get_api", return_value=api), \
         patch.object(service, "get_plan", return_value=plan), \
         patch.object(service, "get_for_organization", return_value=credential), \
         patch.object(service, "find_active", return_value=existing), \
         patch.object(service, "create", return_value=7) as create:
        return service.create_subscription(2, 1, 1, ISSUER), create


class CreateSubscriptionTest(unittest.TestCase):
    def test_creates_subscription_for_other_provider(self):
        (success, result), create = run(PROVIDER_API, {"id": 1})
        self.assertTrue(success)
        self.assertEqual(result, 7)
        create.assert_called_once_with(2, 1, 1)

    def test_rejects_own_api(self):
        (success, _), create = run(dict(PROVIDER_API, provider_org_id=2), {"id": 1})
        self.assertFalse(success)
        create.assert_not_called()

    def test_rejects_unknown_api(self):
        (success, message), _ = run(None, {"id": 1})
        self.assertFalse(success)
        self.assertIn("API", message)

    def test_rejects_unknown_plan(self):
        (success, message), _ = run(PROVIDER_API, None)
        self.assertFalse(success)
        self.assertIn("Plano", message)

    def test_rejects_consumer_without_consumer_role(self):
        provider_only = dict(CREDENTIAL, role_consumer=False)
        (success, message), create = run(PROVIDER_API, {"id": 1}, credential=provider_only)
        self.assertFalse(success)
        self.assertEqual(message, "A organização não está habilitada como consumidora.")
        create.assert_not_called()

    def test_rejects_api_of_inactive_provider(self):
        (success, message), create = run(dict(PROVIDER_API, provider_status="pending"), {"id": 1})
        self.assertFalse(success)
        self.assertEqual(message, "API não encontrada.")
        create.assert_not_called()


if __name__ == "__main__":
    unittest.main()
