from flask import Blueprint, current_app, render_template

from app.auth import current_organization_id, login_required
from app.repositories.credits import get_balance, list_for_organization, totals_for_organization
from app.services.credit_service import package_price_usd


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
