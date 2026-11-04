import unittest
from datetime import date
from unittest.mock import patch

from werkzeug.security import generate_password_hash

from app.services import auth_service

ISSUER = "did:example:authority"
ADMIN = {"id": 1, "email": "admin@dataspace.local", "password_hash": generate_password_hash("admin123")}


def organization(status="active", **extra):
    return {
        "id": 7,
        "did": "did:example:org",
        "email": "org@exemplo.com",
        "password_hash": generate_password_hash("segredo123"),
        "status": status,
        "rejection_reason": None,
        **extra,
    }


def credential(expires_at=date(2099, 12, 31)):
    return {
        "status": "active",
        "issuer_did": ISSUER,
        "subject_did": "did:example:org",
        "role_provider": True,
        "role_consumer": True,
        "expires_at": expires_at,
    }


class AuthServiceTest(unittest.TestCase):
    def authenticate(self, email, password, admin=None, org=None, cred=None):
        with patch.object(auth_service, "get_admin_by_email", return_value=admin) as admins, \
                patch.object(auth_service, "get_organization_by_email", return_value=org) as orgs, \
                patch.object(auth_service, "get_for_organization", return_value=cred):
            result = auth_service.authenticate(email, password, ISSUER)
        self.last_lookups = (admins, orgs)
        return result

    def test_admin_login(self):
        account_type, account, message = self.authenticate("admin@dataspace.local", "admin123", admin=ADMIN)
        self.assertEqual(account_type, "admin")
        self.assertEqual(account, ADMIN)
        self.assertIsNone(message)

    def test_active_organization_login(self):
        org = organization()
        account_type, account, message = self.authenticate("org@exemplo.com", "segredo123", org=org, cred=credential())
        self.assertEqual(account_type, "organization")
        self.assertEqual(account, org)
        self.assertIsNone(message)

    def test_pending_organization_is_blocked(self):
        account_type, account, message = self.authenticate("org@exemplo.com", "segredo123", org=organization("pending"))
        self.assertIsNone(account_type)
        self.assertIsNone(account)
        self.assertEqual(message, "Cadastro em análise. Aguarde a aprovação do administrador.")

    def test_rejected_organization_shows_reason(self):
        org = organization("rejected", rejection_reason="CNPJ divergente")
        _, _, message = self.authenticate("org@exemplo.com", "segredo123", org=org)
        self.assertEqual(message, "Cadastro rejeitado: CNPJ divergente")

    def test_expired_credential_is_blocked(self):
        _, _, message = self.authenticate(
            "org@exemplo.com", "segredo123", org=organization(), cred=credential(date(2000, 1, 1))
        )
        self.assertEqual(message, "A credencial está expirada.")

    def test_wrong_password(self):
        _, _, message = self.authenticate("org@exemplo.com", "errada", org=organization(), cred=credential())
        self.assertEqual(message, "E-mail ou senha inválidos.")

    def test_unknown_email(self):
        account_type, _, message = self.authenticate("ninguem@exemplo.com", "qualquer")
        self.assertIsNone(account_type)
        self.assertEqual(message, "E-mail ou senha inválidos.")

    def test_pending_status_not_revealed_with_wrong_password(self):
        _, _, message = self.authenticate("org@exemplo.com", "errada", org=organization("pending"))
        self.assertEqual(message, "E-mail ou senha inválidos.")

    def test_email_is_normalized(self):
        self.authenticate("  Admin@DataSpace.local ", "admin123", admin=ADMIN)
        admins, _ = self.last_lookups
        admins.assert_called_once_with("admin@dataspace.local")


if __name__ == "__main__":
    unittest.main()
