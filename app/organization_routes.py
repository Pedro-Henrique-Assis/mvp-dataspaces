from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.services.registration_service import register_organization


organization_blueprint = Blueprint("organizations", __name__, url_prefix="/organizations")


@organization_blueprint.get("/new")
def new():
    return render_template("register.html", form={}, errors=[])


@organization_blueprint.post("")
def create():
    ok, errors = register_organization(request.form)
    if not ok:
        return render_template("register.html", form=request.form, errors=errors), 400
    flash("Cadastro enviado. Aguarde a aprovação do administrador.", "success")
    return redirect(url_for("auth.login"))
