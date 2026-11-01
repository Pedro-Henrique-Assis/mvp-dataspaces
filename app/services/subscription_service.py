from app.repositories.apis import get_by_id
from app.repositories.credentials import get_for_organization
from app.repositories.organizations import get_by_id as get_organization
from app.repositories.plans import get_by_id
from app.repositories.subscriptions import create, find_active
from app.services.credential_service import validate_credential


def create_subscription(consumer_id, api_id, plan_id, trusted_issuer):
    consumer = get_organization(consumer_id)
    api = get_by_id(api_id)
    plan = get_by_id(plan_id)
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
    if not plan:
        return False, "Plano não encontrado."
    subscription_id = create(consumer_id, api_id, plan_id)
    return True, subscription_id
