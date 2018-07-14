import os

from app import create_app, db
from app.models.community_resource import CommunityResource
from app.models.user import User
from tests import CommunityResourceFactory
from geoalchemy2 import WKTElement

# Expose flask application from inside connexion.
application = create_app(os.environ.get("DANA_CONFIG", "development")).app


@application.cli.command(with_appcontext=True)
def create_db():
    """Create tables in SQL database from SQLAlchemy models.
    """
    db.engine.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    db.create_all()


@application.cli.command(with_appcontext=True)
def drop_db():
    """Drop all rows and tables from SQL database.
    """
    db.engine.execute("DROP EXTENSION IF EXISTS postgis CASCADE;")
    db.drop_all()


@application.cli.command(with_appcontext=True)
def populate_db():
    """Populate database with default data.
    """
    CommunityResource.populate_db()