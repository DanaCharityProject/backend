from flask import g
from flask_httpauth import HTTPBasicAuth

from .models import User

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    user = User.get_user_by_username(username)

    if not user or not user._verify_password(password):
        return False

    g.current_user = user
    return True
