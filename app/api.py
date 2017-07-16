def post_greeting(body):

    return {
        "greeting": "Hello {}.".format(body["name"])
    }