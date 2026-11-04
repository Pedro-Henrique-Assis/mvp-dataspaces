from functools import wraps

from flask import abort, flash, jsonify, redirect, request, session, url_for


def current_organization_id():
    return session.get("organization_id")


def current_admin_id():
    return session.get("admin_id")


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not current_organization_id():
            if request.path.startswith("/api/"):
                return jsonify({"error": "Autenticação necessária."}), 401
            if current_admin_id():
                flash("Esta página é exclusiva para organizações.", "error")
                return redirect(url_for("admin.organizations"))
            flash("Entre com seu e-mail e senha para continuar.", "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped_view


def admin_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not current_admin_id():
            if current_organization_id():
                abort(403)
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped_view
