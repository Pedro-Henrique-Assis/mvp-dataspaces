from datetime import date, timedelta

from app.repositories.organizations import activate, get_by_id as get_organization, reject


def credential_expiration(today):
    return today + timedelta(days=365)


def approve_organization(organization_id, trusted_issuer, welcome_credits, today=None):
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
    if not activate(organization_id, credential, welcome_credits):
        return False, message
    return True, f"Cadastro aprovado. Credencial emitida e {welcome_credits} créditos de boas-vindas concedidos."


def reject_organization(organization_id, reason):
    reason = (reason or "").strip()
    if not reason:
        return False, "Informe o motivo da rejeição."
    if len(reason) > 255:
        return False, "O motivo deve ter até 255 caracteres."
    if not reject(organization_id, reason):
        return False, "Somente cadastros pendentes podem ser rejeitados."
    return True, "Cadastro rejeitado."
