from werkzeug.security import check_password_hash

from app.repositories.admins import get_by_email as get_admin_by_email
from app.repositories.credentials import get_for_organization
from app.repositories.organizations import get_by_email as get_organization_by_email
from app.services.credential_service import validate_credential


def authenticate(email, password, trusted_issuer):
    email = (email or "").strip().lower()
    password = password or ""

    admin = get_admin_by_email(email)
    if admin and check_password_hash(admin["password_hash"], password):
        return "admin", admin, None

    organization = get_organization_by_email(email)
    if organization and check_password_hash(organization["password_hash"], password):
        if organization["status"] == "pending":
            return None, None, "Cadastro em análise. Aguarde a aprovação do administrador."
        if organization["status"] == "rejected":
            return None, None, f"Cadastro rejeitado: {organization['rejection_reason']}"
        valid, message = validate_credential(
            get_for_organization(organization["id"]), organization, trusted_issuer
        )
        if not valid:
            return None, None, message
        return "organization", organization, None

    return None, None, "E-mail ou senha inválidos."
