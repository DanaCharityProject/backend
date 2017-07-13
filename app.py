import connexion

def post_greeting(body):

    return {
        "greeting": "Hello {}.".format(body["name"])
    }

def create_app():
    app = connexion.FlaskApp(__name__)
    app.add_api("api.yml")

    return app

if __name__ == "__main__":
    app = create_app()

    app.run(port=5000, use_reloader=True, extra_files=["api.yml"])
