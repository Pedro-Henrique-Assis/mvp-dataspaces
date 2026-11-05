from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for

from app.auth import current_organization_id, login_required
from app.repositories.credits import add as add_credits, get_balance, list_for_organization, totals_for_organization
from app.repositories.pix_charges import expire_overdue, get_by_code
from app.services.credit_service import open_top_up, package_price_usd


credits_blueprint = Blueprint("credits", __name__, url_prefix="/credits")

TYPE_LABELS = {
    "bonus": "Bônus",
    "top_up": "Recarga",
    "subscription": "Assinatura",
    "request": "Requisição",
    "earning": "Recebimento",
}


@credits_blueprint.app_context_processor
def credit_balance():
    if current_organization_id():
        return {"credit_balance": get_balance(current_organization_id())}
    return {}


@credits_blueprint.get("")
@login_required
def index():
    organization_id = current_organization_id()
    expire_overdue(organization_id)
    value = current_app.config["CREDIT_VALUE_USD"]
    packages = [
        {"credits": package, "price": package_price_usd(package, value)}
        for package in current_app.config["CREDIT_PACKAGES"]
    ]
    return render_template(
        "credits.html",
        totals=totals_for_organization(organization_id),
        packages=packages,
        transactions=list_for_organization(organization_id),
        type_labels=TYPE_LABELS,
    )


@credits_blueprint.post("/top-ups")
@login_required
def create_top_up():
    config = current_app.config
    valid, result = open_top_up(
        current_organization_id(),
        request.form.get("package"),
        config["CREDIT_PACKAGES"],
        config["CREDIT_VALUE_USD"],
        config["PIX_CHARGE_MINUTES"],
    )
    if not valid:
        flash(result, "error")
        return redirect(url_for("credits.index"))
    return redirect(url_for("credits.show_top_up", code=result))


@credits_blueprint.get("/top-ups/<code>")
@login_required
def show_top_up(code):
    organization_id = current_organization_id()
    expire_overdue(organization_id)
    charge = get_by_code(organization_id, code)
    if charge is None:
        abort(404)
    return render_template("top_up.html", charge=charge)


@credits_blueprint.post("/top-ups/<code>/confirmation")
@login_required
def confirm_payment(code):
    organization_id = current_organization_id()
    charge = get_by_code(organization_id, code)
    if charge is None:
        abort(404)
    add_credits(organization_id, charge["credits"], "top_up", f"Recarga via PIX simulado · {code}")
    flash(f"Pagamento simulado confirmado. +{charge['credits']} créditos.", "success")
    return redirect(url_for("credits.index"))
