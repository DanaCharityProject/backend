from flask import g
from connexion import NoContent

from .auth import auth
from .models import User
from .validators import is_valid_password

@auth.login_required
def get_greeting():

    return {
        "greeting": "Hello {}.".format(g.current_user.username)
    }


@auth.login_required
def post_greeting(body):

    return {
        "greeting": "Hello {}.".format(body["name"])
    }


@auth.login_required
def get_me():
    return g.current_user.to_dict()


@auth.login_required
def get_me_token():
    return {"token": g.current_user.generate_auth_token().decode("ascii")}, 201


def post_me(body):
    user = User(username=body["username"])
    user.password = body["password"]
    user = User.add_user(user)

    if user is None:
        return NoContent, 409

    return user.to_dict(), 201

