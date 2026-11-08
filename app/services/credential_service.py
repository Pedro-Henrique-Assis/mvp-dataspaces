from datetime import date


def validate_credential(credential, organization, trusted_issuer, required_role=None, today=None):
    today = today or date.today()

    if not credential or not organization:
        return False, "Organização ou credencial não encontrada."
    if credential["status"] != "active":
        return False, "A credencial não está ativa."
    if credential["issuer_did"] != trusted_issuer:
        return False, "O emissor da credencial não é confiável."
    if credential["subject_did"] != organization["did"]:
        return False, "O titular da credencial não corresponde à organização."
    if required_role == "consumer" and not credential["role_consumer"]:
        return False, "A organização não está habilitada como consumidora."
    if required_role == "provider" and not credential["role_provider"]:
        return False, "A organização não está habilitada como fornecedora."
    if credential["expires_at"] < today:
        return False, "A credencial está expirada."
    return True, "Credencial válida."