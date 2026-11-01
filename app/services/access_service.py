def authorize_request(subscription, requested_level):
    if not subscription or subscription["status"] != "active":
        return False, "Não existe uma assinatura ativa para esta API."
    if requested_level not in {"basic", "premium"}:
        return False, "Nível de acesso inválido."
    if requested_level == "premium" and subscription["max_access_level"] != "premium":
        return False, "O plano atual não permite acessar dados premium."
    return True, "Acesso autorizado."