import json

from flask import Blueprint, current_app, jsonify, request

from app.auth import current_organization_id, login_required
from app.repositories.apis import get_by_slug
from app.repositories.credentials import get_for_organization
from app.repositories.organizations import get_by_id as get_organization
from app.repositories.usage import register_request
from app.repositories.subscriptions import find_active
from app.services.access_service import authorize_request
from app.services.billing_service import calculate_request_amount
from app.services.credential_service import validate_credential


api_blueprint = Blueprint("api_data", __name__)


@api_blueprint.get("/api/v1/apis/<slug>/data")
@login_required
def api_data(slug):
    level = request.args.get("level", "basic")
    if level not in {"basic", "premium"}:
        return jsonify({"error": "Nível de acesso inválido."}), 400
    api = get_by_slug(slug)
    if not api or api["provider_status"] != "active":
        return jsonify({"error": "API não encontrada."}), 404
    organization_id = current_organization_id()
    valid, message = validate_credential(
        get_for_organization(organization_id),
        get_organization(organization_id),
        current_app.config["TRUSTED_ISSUER_DID"],
    )
    if not valid:
        return jsonify({"error": message}), 403
    subscription = find_active(organization_id, api["id"])
    allowed, message = authorize_request(subscription, level)
    if not allowed:
        return jsonify({"error": message}), 403
    amount = calculate_request_amount(subscription)
    register_request(subscription["id"], level, request.path, amount)
    return jsonify(
        {
            "api": api["name"],
            "provider": api["provider_name"],
            "access_level": level,
            "data": json.loads(api[f"{level}_response"]),
        }
    )
