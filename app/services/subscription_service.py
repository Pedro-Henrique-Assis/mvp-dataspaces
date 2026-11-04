from app.repositories.apis import get_by_id as get_api
from app.repositories.credentials import get_for_organization
from app.repositories.organizations import get_by_id as get_organization
from app.repositories.plans import get_by_id as get_plan
from app.repositories.subscriptions import create, find_active
from app.services.credential_service import validate_credential


def validate_subscription_request(consumer, api, credential_valid, existing_subscription):
    if not credential_valid:
        return False, "A organização não possui uma credencial válida."
    if consumer["id"] == api["provider_org_id"]:
        return False, "A organização não pode assinar a própria API."
    if existing_subscription:
        return False, "Já existe uma assinatura ativa para esta API."
    return True, "Solicitação de assinatura válida."


def create_subscription(consumer_id, api_id, plan_id, trusted_issuer):
    consumer = get_organization(consumer_id)
    api = get_api(api_id)
    plan = get_plan(plan_id)
    if not api:
        return False, "API não encontrada."
    if not plan:
        return False, "Plano não encontrado."
    credential = get_for_organization(consumer_id)
    valid_credential, message = validate_credential(
        credential, consumer, trusted_issuer
    )
    existing = find_active(consumer_id, api_id)
    allowed, message = validate_subscription_request(
        consumer, api, valid_credential, existing
    )
    if not allowed:
        return False, message
    subscription_id = create(consumer_id, api_id, plan_id)
    return True, subscription_id
