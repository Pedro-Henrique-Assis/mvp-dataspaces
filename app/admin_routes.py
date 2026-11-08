import json

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from app.auth import admin_required, current_admin_id
from app.repositories.organizations import count_by_status, list_by_status
from app.services.approval_service import approve_organization, reject_organization


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


@admin_blueprint.post("/organizations/<int:organization_id>/approval")
@admin_required
def approve(organization_id):
    ok, message = approve_organization(
        organization_id,
        current_app.config["TRUSTED_ISSUER_DID"],
        current_app.config["WELCOME_CREDITS"],
    )
    flash(message, "success" if ok else "error")
    return redirect(url_for("admin.organizations"))


@admin_blueprint.post("/organizations/<int:organization_id>/rejection")
@admin_required
def reject(organization_id):
    ok, message = reject_organization(organization_id, request.form.get("reason"))
    flash(message, "success" if ok else "error")
    return redirect(url_for("admin.organizations"))
