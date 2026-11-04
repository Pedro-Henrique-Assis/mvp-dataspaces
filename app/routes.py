from flask import Blueprint, jsonify, render_template

from app.auth import current_organization_id, login_required
from app.repositories.apis import list_public
from app.repositories.subscriptions import list_for_consumer


main_blueprint = Blueprint("main", __name__)


@main_blueprint.get("/")
def home():
    return render_template("home.html", apis=list_public())


@main_blueprint.get("/dashboard")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        apis=list_public(),
        subscriptions=list_for_consumer(current_organization_id()),
    )


@main_blueprint.get("/health")
def health_check():
    return jsonify({"status": "ok"})
