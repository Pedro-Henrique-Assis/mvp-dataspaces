from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from app.auth import current_organization_id, login_required
from app.repositories.apis import list_all
from app.repositories.plans import list_all as list_plans
from app.services.subscription_service import create_subscription


subscriptions_blueprint = Blueprint("subscriptions", __name__, url_prefix="/subscriptions")


@subscriptions_blueprint.get("/")
@login_required
def index():
    return render_template("subscriptions.html", apis=list_all(), plans=list_plans())


@subscriptions_blueprint.post("/create")
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
