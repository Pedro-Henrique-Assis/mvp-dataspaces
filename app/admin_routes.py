from flask import Blueprint, render_template

from app.auth import admin_required, current_admin_id
from app.repositories.organizations import count_by_status


admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")


@admin_blueprint.app_context_processor
def pending_count():
    if current_admin_id():
        return {"pending_count": count_by_status("pending")}
    return {}


@admin_blueprint.get("/organizations")
@admin_required
def organizations():
    return render_template("admin_organizations.html")
