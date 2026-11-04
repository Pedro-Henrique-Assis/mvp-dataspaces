import json

from flask import Blueprint, render_template, request

from app.auth import admin_required, current_admin_id
from app.repositories.organizations import count_by_status, list_by_status


admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")

STATUSES = ["pending", "active", "rejected"]


@admin_blueprint.app_context_processor
def pending_count():
    if current_admin_id():
        return {"pending_count": count_by_status("pending")}
    return {}


def pretty_json(text):
    return json.dumps(json.loads(text), indent=2, ensure_ascii=False)


@admin_blueprint.get("/organizations")
@admin_required
def organizations():
    status = request.args.get("status", "pending")
    if status not in STATUSES:
        status = "pending"
    items = list_by_status(status)
    for organization in items:
        for api in organization["apis"]:
            api["basic_pretty"] = pretty_json(api["basic_response"])
            api["premium_pretty"] = pretty_json(api["premium_response"])
    return render_template("admin_organizations.html", organizations=items, status=status)
