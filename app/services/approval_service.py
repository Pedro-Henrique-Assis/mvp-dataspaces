from datetime import date, timedelta

from app.repositories.organizations import activate, get_by_id as get_organization


def credential_expiration(today):
    return today + timedelta(days=365)


def approve_organization(organization_id, trusted_issuer, today=None):
    today = today or date.today()
    message = "Somente cadastros pendentes podem ser aprovados."
    organization = get_organization(organization_id)
    if not organization or organization["status"] != "pending":
        return False, message

    credential = {
        "issuer_did": trusted_issuer,
        "subject_did": organization["did"],
        "role_provider": organization["role"] in ("provider", "both"),
        "role_consumer": organization["role"] in ("consumer", "both"),
        "issued_at": today,
        "expires_at": credential_expiration(today),
    }
    if not activate(organization_id, credential):
        return False, message
    return True, "Cadastro aprovado."
