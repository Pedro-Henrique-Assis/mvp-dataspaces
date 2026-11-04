from functools import wraps

from flask import flash, jsonify, redirect, request, session, url_for


def current_organization_id():
    return session.get("organization_id")


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not current_organization_id():
            if request.path.startswith("/api/"):
                return jsonify({"error": "Autenticação necessária."}), 401
            flash("Selecione uma organização para continuar.", "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped_view
