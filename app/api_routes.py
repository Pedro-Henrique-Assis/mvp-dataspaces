from flask import Blueprint, current_app, jsonify, request

from app.auth import current_organization_id, login_required
from app.repositories.apis import get_by_slug
from app.repositories.credentials import get_for_organization
from app.repositories.deliveries import list_for_api
from app.repositories.organizations import get_by_id as get_organization
from app.repositories.usage import register_request
from app.repositories.vehicles import list_for_api as list_vehicles
from app.repositories.subscriptions import find_active
from app.services.access_service import authorize_request
from app.services.billing_service import calculate_request_amount
from app.services.credential_service import validate_credential


api_blueprint = Blueprint("api_data", __name__)


def serve_api_data(slug, level, load_data):
    if level not in {"basic", "premium"}:
        return jsonify({"error": "Nível de acesso inválido."}), 400
    api = get_by_slug(slug)
    if not api:
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
    return jsonify({"api": api["name"], "access_level": level, "data": load_data(api["id"], level)})


@api_blueprint.get("/api/entregas/<level>")
@login_required
def deliveries(level):
    return serve_api_data("entregas", level, list_for_api)


@api_blueprint.get("/api/veiculos/<level>")
@login_required
def vehicles(level):
    return serve_api_data("veiculos", level, list_vehicles)
