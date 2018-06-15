import os

from app import create_app, db
from app.models.community_resource import CommunityResource
from app.models.user import User

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
    # create 2 users
    email_1 = "foo"
    password_1 = "bar"
    User.add_user(User.from_dict({
        "email": email_1,
        "password": password_1
    }))
    email_2 = "fizz"
    password_2 = "buzz"
    User.add_user(User.from_dict({
        "email": email_2,
        "password": password_2
    }))

    # create 3 community resources
    SRID = "SRID=4326;"

    charity_number = "1000"
    email = "foo123@mail.com"
    phone_number = "4161234567"
    name = "The Mission"
    contact_name = "John Smith"
    address = "1 Yonge Street"
    coordinates = SRID + "POINT(43.70649 -79.39806)"
    website = "www.test.com"
    image_uri = "http://www.google.com/image.png"

    CommunityResource.add_community_resource(CommunityResource.from_dict({
        "charity_number": charity_number,
        "name": name,
        "address": address,
        "coordinates": coordinates,
        "contact_name": contact_name,
        "email": email,
        "phone_number": phone_number,
        "website": website,
        "image_uri": image_uri
    }))

    charity_number2 = "2000"
    email2 = "foo456@mail.com"
    phone_number2 = "4953234567"
    name2 = "Nearby Charity"
    contact_name2 = "Jacob"
    address2 = "1 Soudan Avenue"
    coordinates2 = SRID + "POINT(43.706 -79.3904)"
    website2 = "www.charitywebsite.com"
    image_uri2 = "http://www.google.com/image2.png"

    CommunityResource.add_community_resource(CommunityResource.from_dict({
        "charity_number": charity_number2,
        "name": name2,
        "address": address2,
        "coordinates": coordinates2,
        "contact_name": contact_name2,
        "email": email2,
        "phone_number": phone_number2,
        "website": website2,
        "image_uri": image_uri2
    }))

    charity_number3 = "3000"
    email3 = "foo789@mail.com"
    phone_number3 = "4162564587"
    name3 = "Another Close Charity"
    contact_name3 = "Pat"
    address3 = "2 Yonge Street"
    coordinates3 = SRID + "POINT(43.70273 -79.39770)"
    website3 = "www.anothercharity.com"
    image_uri3 = "http://www.google.com/image3.png"

    CommunityResource.add_community_resource(CommunityResource.from_dict({
        "charity_number": charity_number3,
        "name": name3,
        "address": address3,
        "coordinates": coordinates3,
        "contact_name": contact_name3,
        "email": email3,
        "phone_number": phone_number3,
        "website": website3,
        "image_uri": image_uri3
    }))

    

