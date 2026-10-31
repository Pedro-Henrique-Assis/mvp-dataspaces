def validate_subscription_request(consumer, api, credential_is_valid, existing):
    if not consumer or not api:
        return False, "Organização ou API não encontrada."
    if consumer["id"] == api["provider_org_id"]:
        return False, "Uma organização não pode assinar a própria API."
    if not credential_is_valid:
        return False, "A credencial da organização não é válida."
    if existing:
        return False, "Já existe uma assinatura ativa para esta API."
    return True, "Assinatura permitida."