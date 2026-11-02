from flask import Blueprint, jsonify, request

from app.auth import current_organization_id, login_required
from app.repositories.apis import get_by_slug
from app.repositories.deliveries import list_for_api
from app.repositories.usage import register_request
from app.repositories.vehicles import list_for_api as list_vehicles
from app.repositories.subscriptions import find_active
from app.services.access_service import authorize_request
from app.services.billing_service import calculate_request_amount


api_blueprint = Blueprint("api_data", __name__)


@api_blueprint.get("/api/entregas/<level>")
@login_required
def deliveries(level):
    if level not in {"basic", "premium"}:
        return jsonify({"error": "Nível de acesso inválido."}), 400
    api = get_by_slug("entregas")
    if not api:
        return jsonify({"error": "API não encontrada."}), 404
    subscription = find_active(current_organization_id(), api["id"])
    if not subscription:
        return jsonify({"error": "Assinatura ativa não encontrada."}), 403
    allowed, message = authorize_request(subscription, level)
    if not allowed:
        return jsonify({"error": message}), 403
    amount = calculate_request_amount(subscription)
    register_request(subscription["id"], level, request.path, amount)
    return jsonify({"api": api["name"], "access_level": level, "data": list_for_api(api["id"], level)})


@api_blueprint.get("/api/veiculos/<level>")
@login_required
def vehicles(level):
    if level not in {"basic", "premium"}:
        return jsonify({"error": "Nível de acesso inválido."}), 400
    api = get_by_slug("veiculos")
    if not api:
        return jsonify({"error": "API não encontrada."}), 404
    subscription = find_active(current_organization_id(), api["id"])
    if not subscription:
        return jsonify({"error": "Assinatura ativa não encontrada."}), 403
    allowed, message = authorize_request(subscription, level)
    if not allowed:
        return jsonify({"error": message}), 403
    amount = calculate_request_amount(subscription)
    register_request(subscription["id"], level, request.path, amount)
    return jsonify({"api": api["name"], "access_level": level, "data": list_vehicles(api["id"], level)})