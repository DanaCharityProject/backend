import os

import connexion
from config import config


def create_app(config_name=None):

    if config_name is None:
        config_name = os.environ.get("DANA_CONFIG", "development")

    app = connexion.FlaskApp(__name__)
    app.app.config.from_object(config[config_name])
    app.add_api("api.yml")

    return app