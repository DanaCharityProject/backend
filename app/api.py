from .auth import auth


@auth.login_required
def post_greeting(body):

    return {
        "greeting": "Hello {}.".format(body["name"])
    }
