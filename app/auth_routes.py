from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from app.repositories.credentials import get_for_organization
from app.repositories.organizations import get_by_id, list_active
from app.services.credential_service import validate_credential


auth_blueprint = Blueprint("auth", __name__)


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    organizations = list_active()
    if request.method == "POST":
        organization_id = request.form.get("organization_id", type=int)
        organization = get_by_id(organization_id) if organization_id else None
        if not organization or organization["status"] != "active":
            flash("Organização não encontrada.", "error")
            return render_template("login.html", organizations=organizations)
        credential = get_for_organization(organization["id"])
        valid, message = validate_credential(
            credential, organization, current_app.config["TRUSTED_ISSUER_DID"]
        )
        if not valid:
            flash(message, "error")
            return render_template("login.html", organizations=organizations)
        session["organization_id"] = organization["id"]
        flash(f"Sessão iniciada para {organization['name']}.", "success")
        return redirect(url_for("main.home"))
    return render_template("login.html", organizations=organizations)


@auth_blueprint.get("/logout")
def logout():
    session.clear()
    flash("Sessão encerrada.", "success")
    return redirect(url_for("main.home"))
