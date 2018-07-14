import os
import shapefile
import pygeoif
import os.path

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
    User.add_user(User.from_dict({
        "email": "dev@danaproject.org",
        "password": "dev"
    }))

    # Below was producing duplicate community_resource_id error

    # CommunityResource.add_community_resource(CommunityResourceFactory())
    # CommunityResource.add_community_resource(CommunityResourceFactory())
    # CommunityResource.add_community_resource(CommunityResourceFactory())
    # CommunityResource.add_community_resource(CommunityResourceFactory())
    # CommunityResource.add_community_resource(CommunityResourceFactory())

    # Shelters
    _parse_shapefile_and_populate_db("/db_info/shelters/shelters_wgs84.shp")
    _parse_shapefile_and_populate_db("/db_info/dropins/TDIN_wgs84.shp")


def _parse_shapefile_and_populate_db(file_path):
    if not os.path.exists(file_path):
        print(file_path + " does not exist")
    else:
        sf = shapefile.Reader(file_path)

        # Create a dict of {<field>: <index>}
        field_dict = {}
        for field in sf.fields:
            field_dict[field[0]] = sf.fields.index(field) - 1

        for shapeRecord in sf.shapeRecords():
            CommunityResource.add_community_resource(CommunityResource.from_dict({
                "community_resource_id": shapeRecord.record[field_dict['OBJECTID']],
                "charity_number": shapeRecord.record[field_dict['OBJECTID']],
                "name": shapeRecord.record[field_dict['NAME']],
                "coordinates": WKTElement(str(pygeoif.Point(pygeoif.as_shape(shapeRecord.shape.__geo_interface__))), 4326),
                "contact_name":"",
                "email":"",
                "phone_number":"",
                "address":"",
                "website":"",
                "image_uri":"",
                "verified": True
                }))