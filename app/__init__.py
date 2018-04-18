import os

import connexion
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from config import config

db = SQLAlchemy()
cors = CORS()


def create_app(config_name=None):

    if config_name is None:
        config_name = os.environ.get("DANA_CONFIG", "development")

    app = connexion.FlaskApp(__name__)
    app.app.config.from_object(config[config_name])

    db.init_app(app.app)
    cors.init_app(app.app)
    app.add_api("api.yml")

    return app
