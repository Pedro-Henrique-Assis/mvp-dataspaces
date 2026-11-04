from flask import Blueprint, render_template

from app.auth import current_organization_id, login_required
from app.repositories.usage import summary_for_consumer


usage_blueprint = Blueprint("usage", __name__, url_prefix="/usage")


@usage_blueprint.get("/")
@login_required
def index():
    return render_template("usage.html", items=summary_for_consumer(current_organization_id()))