from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.repositories.organizations import list_catalog
from app.services.registration_service import register_organization


organization_blueprint = Blueprint("organizations", __name__, url_prefix="/organizations")

SECTORS = {
    "transport": "Transporte",
    "logistics": "Logística",
    "retail": "Varejo",
    "industry": "Indústria",
    "other": "Outro",
}
ROLES = {
    "consumer": "Consumidora",
    "provider": "Fornecedora",
    "both": "Consumidora e fornecedora",
}


@organization_blueprint.get("")
def index():
    return render_template("organizations.html", organizations=list_catalog(), sectors=SECTORS, roles=ROLES)


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
