import unittest

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


if __name__ == "__main__":
    unittest.main()
