import unittest
from datetime import date
from unittest.mock import patch

from app.services import approval_service as service

ISSUER = "did:example:authority"
PENDING = {"id": 5, "did": "did:example:123", "role": "provider", "status": "pending"}


def approve(organization, activated=True):
    with patch.object(service, "get_organization", return_value=organization), \
            patch.object(service, "activate", return_value=activated) as activate:
        result = service.approve_organization(5, ISSUER, today=date(2026, 11, 4))
    return result, activate


class ApproveOrganizationTest(unittest.TestCase):
    def test_credential_expires_in_365_days(self):
        self.assertEqual(service.credential_expiration(date(2026, 11, 4)), date(2027, 11, 4))

    def test_approves_pending_organization_with_credential(self):
        (ok, _), activate = approve(PENDING)
        self.assertTrue(ok)
        org_id, credential = activate.call_args.args
        self.assertEqual(org_id, 5)
        self.assertEqual(credential["issuer_did"], ISSUER)
        self.assertEqual(credential["subject_did"], "did:example:123")
        self.assertEqual(credential["issued_at"], date(2026, 11, 4))
        self.assertEqual(credential["expires_at"], date(2027, 11, 4))

    def test_roles_follow_organization_role(self):
        expected = {"consumer": (False, True), "provider": (True, False), "both": (True, True)}
        for role, (provider, consumer) in expected.items():
            _, activate = approve(dict(PENDING, role=role))
            credential = activate.call_args.args[1]
            self.assertEqual((credential["role_provider"], credential["role_consumer"]), (provider, consumer), role)

    def test_only_pending_can_be_approved(self):
        for organization in [None, dict(PENDING, status="active"), dict(PENDING, status="rejected")]:
            (ok, message), activate = approve(organization)
            self.assertFalse(ok)
            self.assertEqual(message, "Somente cadastros pendentes podem ser aprovados.")
            activate.assert_not_called()

    def test_organization_changed_meanwhile(self):
        (ok, message), _ = approve(PENDING, activated=False)
        self.assertFalse(ok)
        self.assertEqual(message, "Somente cadastros pendentes podem ser aprovados.")


def reject(reason, rejected=True):
    with patch.object(service, "reject", return_value=rejected) as repo_reject:
        return service.reject_organization(5, reason), repo_reject


class RejectOrganizationTest(unittest.TestCase):
    def test_rejects_with_reason(self):
        (ok, _), repo_reject = reject("  CNPJ divergente  ")
        self.assertTrue(ok)
        repo_reject.assert_called_once_with(5, "CNPJ divergente")

    def test_reason_is_required(self):
        for reason in ["", "   ", None]:
            (ok, message), repo_reject = reject(reason)
            self.assertFalse(ok)
            self.assertEqual(message, "Informe o motivo da rejeição.")
            repo_reject.assert_not_called()

    def test_reason_limited_to_255_characters(self):
        (ok, message), repo_reject = reject("x" * 256)
        self.assertFalse(ok)
        self.assertEqual(message, "O motivo deve ter até 255 caracteres.")
        repo_reject.assert_not_called()
        self.assertTrue(reject("x" * 255)[0][0])

    def test_only_pending_can_be_rejected(self):
        (ok, message), _ = reject("motivo", rejected=False)
        self.assertFalse(ok)
        self.assertEqual(message, "Somente cadastros pendentes podem ser rejeitados.")


if __name__ == "__main__":
    unittest.main()
