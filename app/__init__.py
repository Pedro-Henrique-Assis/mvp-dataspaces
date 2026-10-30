from flask import Flask

from app.config import Config
from app.routes import main_blueprint


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    app.register_blueprint(main_blueprint)
    return app