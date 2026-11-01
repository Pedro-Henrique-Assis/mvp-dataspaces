from flask import Blueprint, jsonify

from app.auth import current_organization_id, login_required
from app.repositories.apis import get_by_slug
from app.repositories.deliveries import list_for_api
from app.repositories.vehicles import list_for_api as list_vehicles
from app.repositories.subscriptions import find_active
from app.services.access_service import authorize_request


api_blueprint = Blueprint("api_data", __name__)


@api_blueprint.get("/api/entregas/<level>")
@login_required
def deliveries(level):
    api = get_by_slug("entregas")
    subscription = find_active(current_organization_id(), api["id"])
    allowed, message = authorize_request(subscription, level)
    if not allowed:
        return jsonify({"error": message}), 403
    return jsonify({"api": api["name"], "access_level": level, "data": list_for_api(api["id"], level)})


@api_blueprint.get("/api/veiculos/<level>")
@login_required
def vehicles(level):
    api = get_by_slug("veiculos")
    subscription = find_active(current_organization_id(), api["id"])
    allowed, message = authorize_request(subscription, level)
    if not allowed:
        return jsonify({"error": message}), 403
    return jsonify({"api": api["name"], "access_level": level, "data": list_vehicles(api["id"], level)})