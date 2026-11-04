import json

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from app.repositories.apis import list_for_provider as list_apis_for_provider
from app.repositories.credentials import get_for_organization as get_credential
from app.repositories.organizations import get_by_id as get_organization, list_catalog
from app.repositories.plans import list_all as list_plans
from app.services.registration_service import register_organization, response_fields


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


def describe_fields(api):
    basic = response_fields(json.loads(api["basic_response"]))
    premium = response_fields(json.loads(api["premium_response"]))
    return dict(api, basic_fields=sorted(basic), extra_fields=sorted(premium - basic))


@organization_blueprint.get("/<int:organization_id>")
def show(organization_id):
    organization = get_organization(organization_id)
    if not organization or organization["status"] != "active":
        abort(404)
    apis = [describe_fields(api) for api in list_apis_for_provider(organization_id)]
    return render_template(
        "organization_detail.html",
        organization=organization,
        credential=get_credential(organization_id),
        apis=apis,
        plans=list_plans(),
        sectors=SECTORS,
        roles=ROLES,
    )


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
