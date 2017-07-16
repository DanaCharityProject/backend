from app import create_app

if __name__ == "__main__":
    app = create_app()

    app.run(port=5000, use_reloader=True, extra_files=["app/api.yml"])