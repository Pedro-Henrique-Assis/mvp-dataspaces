from flask import Blueprint, jsonify


main_blueprint = Blueprint("main", __name__)


@main_blueprint.get("/health")
def health_check():
    return jsonify({"status": "ok"})