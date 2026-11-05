from flask import Blueprint, render_template

from app.auth import current_organization_id, login_required
from app.repositories.credits import get_balance


credits_blueprint = Blueprint("credits", __name__, url_prefix="/credits")


@credits_blueprint.app_context_processor
def credit_balance():
    if current_organization_id():
        return {"credit_balance": get_balance(current_organization_id())}
    return {}


@credits_blueprint.get("")
@login_required
def index():
    return render_template("credits.html")
