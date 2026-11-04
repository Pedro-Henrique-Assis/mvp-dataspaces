from flask import Blueprint, render_template


organization_blueprint = Blueprint("organizations", __name__, url_prefix="/organizations")


@organization_blueprint.get("/new")
def new():
    return render_template("register.html", form={}, errors=[])
