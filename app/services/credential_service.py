from datetime import date


def validate_credential(credential, organization, trusted_issuer, today=None):
    today = today or date.today()

    if not credential or not organization:
        return False, "Organização ou credencial não encontrada."
    if credential["status"] != "active":
        return False, "A credencial não está ativa."
    if credential["issuer_did"] != trusted_issuer:
        return False, "O emissor da credencial não é confiável."
    if credential["subject_did"] != organization["did"]:
        return False, "O titular da credencial não corresponde à organização."
    if not credential["role_provider"] or not credential["role_consumer"]:
        return False, "A organização precisa ter os papéis de fornecedora e consumidora."
    if credential["expires_at"] < today:
        return False, "A credencial está expirada."
    return True, "Credencial válida."