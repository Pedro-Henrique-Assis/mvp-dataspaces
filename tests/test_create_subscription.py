import unittest
from datetime import date
from unittest.mock import patch

from app.services import subscription_service as service

ISSUER = "did:example:dataspace-authority"
CONSUMER = {"id": 2, "name": "CargaCerta", "did": "did:example:cargacerta", "credit_balance": 120}
CREDENTIAL = {
    "status": "active",
    "issuer_did": ISSUER,
    "subject_did": "did:example:cargacerta",
    "role_provider": True,
    "role_consumer": True,
    "expires_at": date(2030, 12, 31),
}

PROVIDER_API = {"id": 1, "name": "API de entregas", "provider_org_id": 1, "provider_status": "active"}
PLAN = {"id": 1, "name": "Plano simples", "subscription_price_credits": 100}


def run(api, plan, existing=None, credential=CREDENTIAL, paid=(7, 20)):
    with patch.object(service, "get_organization", return_value=CONSUMER), \
         patch.object(service, "get_api", return_value=api), \
         patch.object(service, "get_plan", return_value=plan), \
         patch.object(service, "get_for_organization", return_value=credential), \
         patch.object(service, "find_active", return_value=existing), \
         patch.object(service, "create_paid", return_value=paid) as create:
        return service.create_subscription(2, 1, 1, ISSUER), create


class CreateSubscriptionTest(unittest.TestCase):
    def test_creates_subscription_for_other_provider(self):
        (success, result), create = run(PROVIDER_API, PLAN)
        self.assertTrue(success)
        self.assertEqual(result, 7)
        consumer_id, provider_id, api_id, plan, descriptions = create.call_args.args
        self.assertEqual((consumer_id, provider_id, api_id, plan), (2, 1, 1, PLAN))
        self.assertEqual(descriptions["consumer"], "Assinatura Plano simples · API de entregas")
        self.assertEqual(descriptions["provider"], "Assinatura de CargaCerta · API de entregas")

    def test_rejects_own_api(self):
        (success, _), create = run(dict(PROVIDER_API, provider_org_id=2), PLAN)
        self.assertFalse(success)
        create.assert_not_called()

    def test_rejects_unknown_api(self):
        (success, message), _ = run(None, PLAN)
        self.assertFalse(success)
        self.assertIn("API", message)

    def test_rejects_unknown_plan(self):
        (success, message), _ = run(PROVIDER_API, None)
        self.assertFalse(success)
        self.assertIn("Plano", message)

    def test_rejects_consumer_without_consumer_role(self):
        provider_only = dict(CREDENTIAL, role_consumer=False)
        (success, message), create = run(PROVIDER_API, PLAN, credential=provider_only)
        self.assertFalse(success)
        self.assertEqual(message, "A organização não está habilitada como consumidora.")
        create.assert_not_called()

    def test_rejects_when_credits_are_not_enough(self):
        (success, message), create = run(PROVIDER_API, PLAN, paid=(None, 20))
        self.assertFalse(success)
        self.assertEqual(
            message,
            "Créditos insuficientes: a assinatura custa 100 créditos e o saldo é 20.",
        )
        create.assert_called_once()

    def test_rejected_requests_do_not_touch_credits(self):
        for api, plan in [(None, PLAN), (PROVIDER_API, None), (dict(PROVIDER_API, provider_org_id=2), PLAN)]:
            _, create = run(api, plan)
            create.assert_not_called()

    def test_rejects_api_of_inactive_provider(self):
        (success, message), create = run(dict(PROVIDER_API, provider_status="pending"), PLAN)
        self.assertFalse(success)
        self.assertEqual(message, "API não encontrada.")
        create.assert_not_called()


if __name__ == "__main__":
    unittest.main()
