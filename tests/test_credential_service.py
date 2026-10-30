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


if __name__ == "__main__":
    unittest.main()