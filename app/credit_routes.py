from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from app.auth import current_organization_id, login_required
from app.repositories.credits import add as add_credits, get_balance, list_for_organization, totals_for_organization
from app.services.credit_service import fake_pix_code, package_price_usd, validate_package


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


@credits_blueprint.get("/top-ups/new")
@login_required
def new_top_up():
    valid, package = validate_package(request.args.get("package"), current_app.config["CREDIT_PACKAGES"])
    if not valid:
        flash(package, "error")
        return redirect(url_for("credits.index"))
    return render_template(
        "top_up.html",
        package=package,
        price=package_price_usd(package, current_app.config["CREDIT_VALUE_USD"]),
        pix_code=fake_pix_code(current_organization_id(), package),
    )


@credits_blueprint.post("/top-ups")
@login_required
def create_top_up():
    valid, package = validate_package(request.form.get("package"), current_app.config["CREDIT_PACKAGES"])
    if not valid:
        flash(package, "error")
        return redirect(url_for("credits.index"))
    add_credits(current_organization_id(), package, "top_up", "Recarga via PIX simulado")
    flash(f"Pagamento simulado confirmado. +{package} créditos.", "success")
    return redirect(url_for("credits.index"))
