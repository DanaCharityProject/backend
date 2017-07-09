import connexion

def post_greeting(body):

    return { 
        "greeting": "Hello {}.".format(body["name"])
    }

if __name__ == "__main__":
    app = connexion.FlaskApp(__name__)
    app.add_api("api.yml")
    app.run(port=5000, use_reloader=True, extra_files=["api.yml"])