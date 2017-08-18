import os

import connexion
from flask_sqlalchemy import SQLAlchemy

from config import config

db = SQLAlchemy()

from . import user_model, user_manager_model, community_resource_model, exception_models


def create_app(config_name=None):

    if config_name is None:
        config_name = os.environ.get("DANA_CONFIG", "development")

    app = connexion.FlaskApp(__name__)
    app.app.config.from_object(config[config_name])

    db.init_app(app.app)
    app.add_api("api.yml")

    return app
