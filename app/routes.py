from flask import Blueprint, jsonify, render_template


main_blueprint = Blueprint("main", __name__)


@main_blueprint.get("/")
def home():
    return render_template("home.html")


@main_blueprint.get("/health")
def health_check():
    return jsonify({"status": "ok"})