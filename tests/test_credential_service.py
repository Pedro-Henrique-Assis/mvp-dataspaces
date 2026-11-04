import unittest
from datetime import date

from app.services.credential_service import validate_credential


class CredentialServiceTest(unittest.TestCase):
    def setUp(self):
        self.organization = {"did": "did:example:org-a"}
        self.credential = {
            "status": "active",
            "issuer_did": "did:example:authority",
            "subject_did": "did:example:org-a",
            "role_provider": True,
            "role_consumer": True,
            "expires_at": date(2030, 12, 31),
        }

    def test_accepts_valid_credential(self):
        valid, message = validate_credential(
            self.credential,
            self.organization,
            "did:example:authority",
            today=date(2030, 1, 1),
        )
        self.assertTrue(valid)
        self.assertEqual(message, "Credencial válida.")

    def test_rejects_expired_credential(self):
        valid, _ = validate_credential(
            self.credential,
            self.organization,
            "did:example:authority",
            today=date(2031, 1, 1),
        )
        self.assertFalse(valid)

    def validate(self, required_role, **roles):
        credential = {**self.credential, **roles}
        return validate_credential(
            credential,
            self.organization,
            "did:example:authority",
            required_role=required_role,
            today=date(2030, 1, 1),
        )

    def test_accepts_single_role_without_requirement(self):
        valid, _ = self.validate(None, role_provider=False)
        self.assertTrue(valid)

    def test_consumer_role_is_required(self):
        valid, message = self.validate("consumer", role_consumer=False)
        self.assertFalse(valid)
        self.assertEqual(message, "A organização não está habilitada como consumidora.")

    def test_provider_role_is_required(self):
        valid, message = self.validate("provider", role_provider=False)
        self.assertFalse(valid)
        self.assertEqual(message, "A organização não está habilitada como fornecedora.")

    def test_required_role_present(self):
        valid, _ = self.validate("consumer", role_provider=False)
        self.assertTrue(valid)


if __name__ == "__main__":
    unittest.main()