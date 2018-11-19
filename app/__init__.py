import os

import connexion
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_rbac import RBAC

from config import config

db = SQLAlchemy()
cors = CORS()
rbac = RBAC()

# These imports are here because they depend on db being initialized above
from .models import role
from .models import user

def create_app(config_name=None):

    if config_name is None:
        config_name = os.environ.get("DANA_CONFIG", "development")

    app = connexion.FlaskApp(__name__)
    app.app.config.from_object(config[config_name])

    db.init_app(app.app)
    cors.init_app(app.app)
    rbac.init_app(app.app)
    app.add_api("api.yml")

    rbac.set_role_model(role.Role)
    rbac.set_user_model(user.User)

    return app
