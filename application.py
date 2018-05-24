import os

from app import create_app, db

# Expose flask application from inside connexion.
application = create_app(os.environ.get("DANA_CONFIG", "development")).app


@application.cli.command(with_appcontext=True)
def create_db():
    """Create tables in SQL database from SQLAlchemy models.
    """
    db.create_all()


@application.cli.command(with_appcontext=True)
def drop_db():
    """Drop all rows and tables from SQL database.
    """
    db.drop_all()
