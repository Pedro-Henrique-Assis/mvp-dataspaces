from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from app.auth import current_organization_id, login_required
from app.repositories.apis import list_available_for
from app.repositories.credentials import get_for_organization as get_credential
from app.repositories.organizations import get_by_id as get_organization
from app.repositories.plans import list_all as list_plans
from app.services.credential_service import validate_credential
from app.services.subscription_service import create_subscription


subscriptions_blueprint = Blueprint("subscriptions", __name__, url_prefix="/subscriptions")


@subscriptions_blueprint.get("")
@login_required
def index():
    organization_id = current_organization_id()
    can_subscribe, message = validate_credential(
        get_credential(organization_id),
        get_organization(organization_id),
        current_app.config["TRUSTED_ISSUER_DID"],
        required_role="consumer",
    )
    apis = list_available_for(organization_id)
    selected_id = request.args.get("api_id", type=int)
    apis.sort(key=lambda api: api["id"] != selected_id)
    return render_template(
        "subscriptions.html",
        apis=apis,
        plans=list_plans(),
        selected_id=selected_id,
        can_subscribe=can_subscribe,
        message=message,
    )


@subscriptions_blueprint.post("")
@login_required
def create():
    api_id = request.form.get("api_id", type=int)
    plan_id = request.form.get("plan_id", type=int)
    if not api_id or not plan_id:
        flash("Selecione uma API e um plano.", "error")
        return redirect(url_for("subscriptions.index"))
    success, result = create_subscription(
        current_organization_id(),
        api_id,
        plan_id,
        current_app.config["TRUSTED_ISSUER_DID"],
    )
    flash("Assinatura criada." if success else result, "success" if success else "error")
    return redirect(url_for("main.dashboard"))
