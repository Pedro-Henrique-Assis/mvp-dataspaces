from flask import Flask

from app.admin_routes import admin_blueprint
from app.api_routes import api_blueprint
from app.auth_routes import auth_blueprint
from app.config import Config
from app.errors import register_error_handlers
from app.routes import main_blueprint
from app.subscription_routes import subscriptions_blueprint
from app.usage_routes import usage_blueprint


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(subscriptions_blueprint)
    app.register_blueprint(usage_blueprint)
    register_error_handlers(app)
    return app