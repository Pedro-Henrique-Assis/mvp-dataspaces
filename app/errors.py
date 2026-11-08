from flask import jsonify, render_template, request


def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Recurso não encontrado."}), 404
        return render_template("error.html", message="Página não encontrada."), 404

    @app.errorhandler(500)
    def internal_error(error):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Erro interno da aplicação."}), 500
        return render_template("error.html", message="Erro interno da aplicação."), 500