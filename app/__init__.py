from flask import Flask

from . import db as db_module


def create_app() -> Flask:
    app = Flask(__name__)
    db_module.init_db()

    from .routes import bp

    app.register_blueprint(bp)
    return app
