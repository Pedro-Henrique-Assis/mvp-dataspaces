import unittest
from unittest.mock import patch

from werkzeug.security import check_password_hash

from app.services import registration_service as service
from app.services.registration_service import validate_organization


def valid_form(**changes):
    form = {
        "name": "Rota Certa Ltda",
        "cnpj": "11.222.333/0001-81",
        "email": "contato@rotacerta.com.br",
        "password": "senha1234",
        "password_confirmation": "senha1234",
        "sector": "transport",
        "role": "consumer",
        "contact_name": "Maria Souza",
        "description": "",
        "website": "",
        "accepted_terms": "on",
    }
    form.update(changes)
    return form


class ValidateOrganizationTest(unittest.TestCase):
    def test_valid_form_has_no_errors(self):
        self.assertEqual(validate_organization(valid_form()), [])

    def test_required_fields(self):
        for field in ["name", "cnpj", "email", "password", "sector", "role", "contact_name"]:
            errors = validate_organization(valid_form(**{field: ""}))
            self.assertTrue(errors, field)

    def test_invalid_cnpj(self):
        errors = validate_organization(valid_form(cnpj="11222333000182"))
        self.assertIn("CNPJ inválido.", errors)

    def test_email_needs_at_and_domain(self):
        for email in ["semarroba.com", "a@", "a@semponto", "@dominio.com"]:
            errors = validate_organization(valid_form(email=email))
            self.assertIn("E-mail inválido.", errors, email)

    def test_short_password(self):
        errors = validate_organization(valid_form(password="curta", password_confirmation="curta"))
        self.assertIn("A senha deve ter pelo menos 8 caracteres.", errors)

    def test_password_confirmation_must_match(self):
        errors = validate_organization(valid_form(password_confirmation="outra1234"))
        self.assertIn("A confirmação da senha não confere.", errors)

    def test_sector_and_role_must_be_in_list(self):
        self.assertIn("Setor inválido.", validate_organization(valid_form(sector="agro")))
        self.assertIn("Papel inválido.", validate_organization(valid_form(role="admin")))

    def test_terms_must_be_accepted(self):
        errors = validate_organization(valid_form(accepted_terms=""))
        self.assertIn("É necessário aceitar os termos de uso.", errors)

    def test_column_size_limits(self):
        errors = validate_organization(valid_form(name="x" * 121, website="y" * 161, description="z" * 256))
        self.assertIn("Razão social deve ter até 120 caracteres.", errors)
        self.assertIn("Site deve ter até 160 caracteres.", errors)
        self.assertIn("Descrição deve ter até 255 caracteres.", errors)


class RegisterOrganizationTest(unittest.TestCase):
    def register(self, form, email_org=None, email_admin=None, cnpj_org=None):
        with patch.object(service, "get_organization_by_email", return_value=email_org),                 patch.object(service, "get_admin_by_email", return_value=email_admin),                 patch.object(service, "get_organization_by_cnpj", return_value=cnpj_org),                 patch.object(service, "create_with_api") as create:
            return service.register_organization(form), create

    def test_saves_pending_organization_with_clean_data(self):
        form = valid_form(email=" Contato@RotaCerta.com.br ")
        (ok, errors), create = self.register(form)
        self.assertTrue(ok)
        self.assertEqual(errors, [])
        org, api = create.call_args.args
        self.assertEqual(org["cnpj"], "11222333000181")
        self.assertEqual(org["email"], "contato@rotacerta.com.br")
        self.assertEqual(org["did"], "did:example:11222333000181")
        self.assertTrue(check_password_hash(org["password_hash"], "senha1234"))
        self.assertNotIn("password", org)
        self.assertIsNone(api)

    def test_invalid_form_saves_nothing(self):
        (ok, errors), create = self.register(valid_form(cnpj="123"))
        self.assertFalse(ok)
        self.assertIn("CNPJ inválido.", errors)
        create.assert_not_called()

    def test_duplicate_email_in_organizations(self):
        (ok, errors), create = self.register(valid_form(), email_org={"id": 1})
        self.assertFalse(ok)
        self.assertEqual(errors, ["E-mail já cadastrado."])
        create.assert_not_called()

    def test_duplicate_email_in_admins(self):
        (_, errors), _ = self.register(valid_form(), email_admin={"id": 1})
        self.assertEqual(errors, ["E-mail já cadastrado."])

    def test_duplicate_cnpj(self):
        (_, errors), create = self.register(valid_form(), cnpj_org={"id": 1})
        self.assertEqual(errors, ["CNPJ já cadastrado."])
        create.assert_not_called()


if __name__ == "__main__":
    unittest.main()
