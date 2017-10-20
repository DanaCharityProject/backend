from flask import g
from flask_httpauth import HTTPBasicAuth

from .models.user import User
from .models.rbac import Role

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    user = User.get_user_by_username(username)

    if not user or not user.verify_password(password):
        return False

    g.current_user = user
    return True


def accept_roles(roles):
    def _accept_roles(f):
        def wrapper(*args, **kwargs):
            role = get_current_role()

            if Role.is_allowed(role, roles):
                return f(*args, **kwargs)

        return wrapper
    return _accept_roles


def get_current_role():
    return g.current_role
