from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from app.services.auth_service import authenticate


auth_blueprint = Blueprint("auth", __name__)


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        account_type, account, message = authenticate(
            request.form.get("email"),
            request.form.get("password"),
            current_app.config["TRUSTED_ISSUER_DID"],
        )
        if not account_type:
            flash(message, "error")
            return render_template("login.html")
        session.clear()
        if account_type == "admin":
            session["admin_id"] = account["id"]
            return redirect(url_for("admin.organizations"))
        session["organization_id"] = account["id"]
        flash(f"Sessão iniciada para {account['name']}.", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("login.html")


@auth_blueprint.get("/logout")
def logout():
    session.clear()
    flash("Sessão encerrada.", "success")
    return redirect(url_for("main.home"))
