from flask import g
from flask_httpauth import HTTPBasicAuth

from .models.user import User

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    user = User.get_user_by_username(username)

    if not user or not user.verify_password(password):
        return False

    g.current_user = user
    return True
