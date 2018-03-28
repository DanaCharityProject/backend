import os

from app import create_app, db

if __name__ == "__main__":
    app = create_app(os.environ.get("DANA_CONFIG", "development"))

    with app.app.app_context():
        db.drop_all()
        db.create_all()

    app.run(port=5000, use_reloader=True, extra_files=["app/api.yml"])
