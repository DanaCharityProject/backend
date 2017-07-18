from flask import g

from .auth import auth
from .models import User


@auth.login_required
def post_greeting(body):

    return {
        "greeting": "Hello {}.".format(body["name"])
    }


@auth.login_required
def get_me():
    return g.current_user.to_dict()


def post_me(body):
    user = User(username=body["username"])
    user.password = body["password"]
    user = User.add_user(user)

    return user.to_dict(), 201
