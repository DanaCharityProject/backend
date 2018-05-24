from flask import g
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth

from .models.user import User

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

auth = MultiAuth(basic_auth, token_auth)

@basic_auth.verify_password
def verify_password(username, password):
    user = User.get_user_by_username(username)

    if not user or not user.verify_password(password):
        return False

    g.current_user = user
    g.current_role = user.role

    return True

@token_auth.verify_token
def verify_token(token):
    user = User.get_user_by_token(token)

    if not user:
        return False

    g.current_user = user
    g.current_role = user.role

    return True

def current_user():
    return g.current_user

def current_role():
    return g.current_role
