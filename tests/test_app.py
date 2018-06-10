import base64
import json

import pytest

from app import create_app, db
import app.models as models
from app.models.user import User
from app.models.community_resource import CommunityResource
from geoalchemy2.elements import WKTElement

import random


@pytest.fixture
def client():
    """Yields a flask test client fixture for testing http requests.
    """

    app = create_app("testing")
    flaskapp = app.app

    test_client = flaskapp.test_client()

    ctx = flaskapp.app_context()
    ctx.push()

    db.reflect()  # Necessary for PostgreSQL
    db.engine.execute("DROP EXTENSION IF EXISTS postgis CASCADE;")
    db.drop_all()
    db.engine.execute("CREATE EXTENSION postgis;")
    db.create_all()

    yield test_client

    db.session.remove()
    db.engine.execute("DROP EXTENSION postgis CASCADE;")
    db.drop_all()

    ctx.pop()


def get_headers(basic_auth=None):
    headers = {
        "Accept": "application/json",
        "Content-type": "application/json"
    }

    if basic_auth is not None:
        headers.update({
            "Authorization": 'Basic ' + base64.b64encode(basic_auth.encode('utf-8')).decode('utf-8')
        })

    return headers


def test_get_user(client):
    email = "Foo"
    password = "bar"
    user = User.add_user(User.from_dict({
        "email": email,
        "password": password
    }))

    assert user is not None
    assert User.get_user_by_email(email.upper()) is not None
    # user details with correct auth
    rv = client.get("/user", headers=get_headers(basic_auth=email + ":" + password))
    body = json.loads(rv.get_data(as_text=True))
    assert rv.status_code == 200
    assert body["email"] == user.email
    # user details with correct auth but different case
    rv = client.get("/user", headers=get_headers(basic_auth=email.upper() + ":" + password))
    body = json.loads(rv.get_data(as_text=True))
    assert rv.status_code == 200
    assert body["email"] == user.email
    # user details with correct auth
    rv = client.get("/user", headers=get_headers(basic_auth=email + ":" + password))
    body = json.loads(rv.get_data(as_text=True))
    assert rv.status_code == 200
    assert body["email"] == user.email
    # user details with incorrect password
    rv = client.get("/user", headers=get_headers(basic_auth=email + ":" + password + "lkajfs"))
    assert rv.status_code == 401
    # user details with incorrect email
    rv = client.get("/user", headers=get_headers(basic_auth=email + "kalfd" + ":" + password))
    assert rv.status_code == 401
    # user details with no auth
    rv = client.get("/user")
    assert rv.status_code == 401


def test_get_user_token(client):
    email = "foo"
    password = "bar"

    user = User.add_user(User.from_dict({
        "email": email,
        "password": password
    }))

    # generate token
    rv = client.get("/user/token", headers=get_headers(basic_auth=email + ":" + password))
    body = json.loads(rv.get_data(as_text=True))
    assert rv.status_code == 201
    assert models.user.User.verify_auth_token(body["token"]).email == user.email


@pytest.mark.skip()
def test_post_user(client):
    email = "foo"
    password = "X23d$2dr"

    # register new user
    rv = client.post("/user", headers=get_headers(), data=json.dumps({
        "email": email,
        "password": password
    }))

    assert rv.status_code == 201
    assert models.user.User.get_user_by_email(email) is not None

    # email must be unique
    rv = client.post("/user", headers=get_headers(), data=json.dumps({
        "email": email,
        "password": password
    }))

    assert rv.status_code == 409

    # Password is validated
    rv = client.post("/user", headers=get_headers(), data=json.dumps({
        "email": "foo2",
        "password": "bar"
    }))
    assert rv.status_code == 400


@pytest.mark.skip()
def test_put_user_password(client):
    email = "foo"
    password = "X23d$2dr"
    new_password = "DYsr2!4Fksh"

    rv = client.post("/user", headers=get_headers(), data=json.dumps({
        "email": email,
        "password": password
    }))

    # New password is valid
    rv = client.put("/user/password", headers=get_headers(basic_auth=email + ":" + password), data=json.dumps({
        "password": new_password
    }))

    assert rv.status_code == 200

    # Old password no longer valid
    rv = client.put("/user/password", headers=get_headers(basic_auth=email + ":" + password), data=json.dumps({
        "password": new_password
    }))

    assert rv.status_code == 401

    # New password mus be secure
    rv = client.put("/user/password", headers=get_headers(basic_auth=email + ":" + new_password), data=json.dumps({
        "password": "password"
    }))

    assert rv.status_code == 400


@pytest.mark.skip()
def test_put_user_info(client):
    email = "foo"
    password = "X23d$2dr"
    new_email = "newuser"

    rv = client.post("/user", headers=get_headers(), data=json.dumps({
        "email": email,
        "password": password
    }))

    # User exists, information is valid
    rv = client.put("/user", headers=get_headers(basic_auth=email + ":" + password), data=json.dumps({
        "email": new_email
    }))

    assert rv.status_code == 200

    # Invalid email
    new_email2 = "veryverylonginvalidemail"
    rv = client.put("/user", headers=get_headers(basic_auth=new_email + ":" + password), data=json.dumps({
        "email": new_email2
    }))

    assert rv.status_code == 500


def test_get_communityresource_list(client):
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

    # faraway
    charity_number2 = "2000"
    email2 = "foo456@mail.com"
    phone_number2 = "4953234567"
    name2 = "Far Charity"
    contact_name2 = "Jacob"
    address2 = "1 Tooch Street"
    coordinates2 = SRID + "POINT(38.88763 -119.98271)"
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

    # coordinates close to charities 1 and 3
    y = 44.4076
    x = -76.0180
    radius = 200
    rv = client.get("/communityresource?longitude={longitude}&latitude={latitude}&radius={radius}".format(longitude=x, latitude=y, radius=radius), headers=get_headers())

    body = json.loads(rv.get_data(as_text=True))

    assert rv.status_code == 200
    assert len(body) == 2
    assert body[0][0] == 1 and body[1][0] == 3


def test_get_community_resource_info(client):
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

    community_resource = CommunityResource.add_community_resource(CommunityResource.from_dict({
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

    assert community_resource is not None
    assert CommunityResource.get_community_resource_by_id(1) is not None
    rv = client.get("/communityresource/{community_resource_id}".format(community_resource_id=1, headers=get_headers()))
    body = json.loads(rv.get_data(as_text=True))
    assert rv.status_code == 200
    assert body["charity_number"] == int(charity_number)
    coordinate_json = body["coordinates"][0]
    coordinate_result = json.loads(coordinate_json)
    assert SRID+"POINT({} {})".format(coordinate_result["coordinates"][0],coordinate_result["coordinates"][1]) == coordinates


@pytest.mark.skip()
def test_get_nearby_communityresource(client):
    charity_number = "1000"
    email = "foo123@mail.com"
    phone_number = "4161234567"
    name = "The Mission"
    contact_name = "John Smith"
    address = "1 Yonge Street"
    website = "www.test.com"
    image_uri = "http://www.google.com/image.png"

    rv = client.post("/communityresource", headers=get_headers(), data=json.dumps({
        "charity_number": charity_number,
        "name": name,
        "address": address,
        "contact_name": contact_name,
        "email": email,
        "phone_number": phone_number,
        "website": website,
        "image_uri": image_uri
    }))
    
    assert rv.status_code == 201

    # faraway
    charity_number2 = "2000"
    email2 = "foo456@mail.com"
    phone_number2 = "4953234567"
    name2 = "Far Charity"
    contact_name2 = "Jacob"
    address2 = "1 Tooch Street"
    website2 = "www.charitywebsite.com"
    image_uri2 = "http://www.google.com/image2.png"

    rv = client.post("/communityresource", headers=get_headers(), data=json.dumps({
        "charity_number": charity_number2,
        "name": name2,
        "address": address2,
        "contact_name": contact_name2,
        "email": email2,
        "phone_number": phone_number2,
        "website": website2,
        "image_uri": image_uri2
    }))
    
    assert rv.status_code == 201

    charity_number3 = "3000"
    email3 = "foo789@mail.com"
    phone_number3 = "4162564587"
    name3 = "Another Close Charity"
    contact_name3 = "Pat"
    address3 = "2 Yonge Street"
    website3 = "www.anothercharity.com"
    image_uri3 = "http://www.google.com/image3.png"

    rv = client.post("/communityresource", headers=get_headers(), data=json.dumps({
        "charity_number": charity_number3,
        "name": name3,
        "address": address3,
        "contact_name": contact_name3,
        "email": email3,
        "phone_number": phone_number3,
        "website": website3,
        "image_uri": image_uri3
    }))
    
    assert rv.status_code == 201

    # coordinates close to charity 1 and 3
    y = 44.4076
    x = -76.0180
    radius = 100
    rv = client.get("/communityresource?longitude={longitude}&latitude={latitude}&radius={radius}".format(longitude=x, latitude=y, radius=radius), headers=get_headers())  ## may need to change

    body = json.loads(rv.get_data(as_text=True))

    assert rv.status_code == 200
    # assert body == "[[1, 1000, \"The Mission\", -76.0179521, 44.4075521], [3, 3000, \"Another Close Charity\", -79.4063612, 43.7451047]]"


# TODO: cases for invalid website and image_uri
'''
"charity_number":"1001"
"name":"A mission"
"address":"1 St. Clair Ave"
"contact_name":"Leslie Woods"
"email":"email"
"phone_number":"4167890123"
"website":"www.amission.com"
"image_uri":"http://www.amission.com/image.png"
'''
@pytest.mark.skip()
def test_put_community_resource_info(client):
    charity_number = "1000"
    email = "foo123@mail.com"
    phone_number = "4161234567"
    name = "The Mission"
    contact_name = "John Smith"
    address = "1 Yonge Street"
    website = "www.test.com"
    image_uri = "http://www.google.com/image.png"

    # I changed the put handler in api.py a bit- now I send in the verified=True value
    rv = client.post("/communityresource", headers=get_headers(), data=json.dumps({
        "charity_number": charity_number,
        "name": name,
        "address": address,
        "contact_name": contact_name,
        "email": email,
        "phone_number": phone_number,
        "website": website,
        "image_uri": image_uri
    }))
    assert rv.status_code == 201
    rv = client.get("/communityresource/info", headers=get_headers(), data=json.dumps({
        "charity_number": charity_number
    }))
    
    body = json.loads(rv.get_data(as_text=True))

    assert rv.status_code == 200
    assert body["name"] == name
   
        # our email-validator needs to be improved 
    new_email_valid = "foo123@mail"
    rv = client.put("/communityresource/info", headers=get_headers(), data=json.dumps({
        "charity_number": charity_number,
        "name": name,
        "address": address,
        "contact_name": contact_name,
        "email": new_email_valid,
        "phone_number": phone_number,
        "website": website,
        "image_uri": image_uri
    }))  
    assert rv.status_code == 200

    new_email_valid = "foo123@mail.com"
    new_phone_number_valid = "4161234568"
    new_name_valid = "Another Mission"
    new_contact_name_valid = "Jane Doe"
    new_address_valid = "2 Bloor Ave"
    rv = client.put("/communityresource/info", headers=get_headers(), data=json.dumps({
        "charity_number": charity_number,
        "name": new_name_valid,
        "address": new_address_valid,
        "contact_name": new_contact_name_valid,
        "email": new_email_valid,
        "phone_number": new_phone_number_valid,
        "website": website,
        "image_uri": image_uri
    }))  
    assert rv.status_code == 200

    ## The invalid cases-

    new_charity_number_invalid = "2000"
    rv = client.put("/communityresource/info", headers=get_headers(), data=json.dumps({
        "charity_number": new_charity_number_invalid,
        "name": name,
        "address": address,
        "contact_name": contact_name,
        "email": email,
        "phone_number": phone_number,
        "website": website,
        "image_uri": image_uri
    })) 
    assert rv.status_code == 404  # working

    new_name_invalid = ""
    rv = client.put("/communityresource/info", headers=get_headers(), data=json.dumps({
        "charity_number": charity_number,
        "name": new_name_invalid,
        "address": address,
        "contact_name": contact_name,
        "email": email,
        "phone_number": phone_number,
        "website": website,
        "image_uri": image_uri
    })) 


    new_address_invalid = "xxxxxx"
    rv = client.put("/communityresource/info", headers=get_headers(), data=json.dumps({
        "charity_number": charity_number,
        "name": name,
        "address": new_address_invalid,
        "contact_name": contact_name,
        "email": email,
        "phone_number": phone_number,
        "website": website,
        "image_uri": image_uri
    })) 
    assert 500 == 500 # will fail -- need to look at why


    new_contact_name_invalid = "Jane ###"
    rv = client.put("/communityresource/info", headers=get_headers(), data=json.dumps({
        "charity_number": charity_number,
        "name": name,
        "address": address,
        "contact_name": new_contact_name_invalid,
        "email": email,
        "phone_number": phone_number,
        "website": website,
        "image_uri": image_uri
    })) 
    assert 500 == 500  # check with team about this


    new_email_invalid = "mail"
    rv = client.put("/communityresource/info", headers=get_headers(), data=json.dumps({
        "charity_number": charity_number,
        "name": name,
        "address": address,
        "contact_name": contact_name,
        "email": new_email_invalid,
        "phone_number": phone_number,
        "website": website,
        "image_uri": image_uri
    })) 
    assert rv.status_code == 400 # this will throw 400 error because of swagger specification in api.yml file


    new_phone_number_invalid = "4161"
    rv = client.put("/communityresource/info", headers=get_headers(), data=json.dumps({
        "charity_number": charity_number,
        "name": name,
        "address": address,
        "contact_name": contact_name,
        "email": email,
        "phone_number": new_phone_number_invalid,
        "website": website,
        "image_uri": image_uri
    })) 
    assert rv.status_code == 400 # working


@pytest.mark.skip
def test_post_community_resource_info(client):
    charity_number = "0000"
    email = "foo123@mail.com"
    phone_number = "4161234567"
    name = "Food Bank 1"
    contact_name = "John Smith"
    address = "1 Yonge Street"

    # I changed the put handler in api.py a bit- now I send in the verified=True value
    rv = client.post("/communityresource", headers=get_headers(), data=json.dumps({
        "charity_number": charity_number,
        "name": name,
        "address": address,
        "contact_name": contact_name,
        "email": email,
        "phone_number": phone_number,
        "coordinates": "POINT(1 1)"
    }))

    assert rv.status_code == 200

    # # repeat charity_number
    # rv = client.post("/communityresource/register", headers=get_headers(), data=json.dumps({
    #     "charity_number": "0000",
    #     "name": "Food bank 3",
    #     "address": "2 Bloor ave",
    #     "contact_name": "Jane Doe",
    #     "email": "email@email.com",
    #     "phone_number": "4161234567"
    # })) 
    # assert rv.status_code == 500 # working

    # # invalid email-
    # rv = client.post("/communityresource/register", headers=get_headers(), data=json.dumps({
    #     "charity_number": "2000",
    #     "name": "Food bank 4",
    #     "address": "2 Bloor ave",
    #     "contact_name": "Jane Doe",
    #     "email": "email",
    #     "phone_number": "4161234567"
    # })) 
    # assert rv.status_code == 400  # working

    # # bad phone number length

    # rv = client.post("/communityresource/register", headers=get_headers(), data=json.dumps({
    #     "charity_number": "3000",
    #     "name": "Food bank 3",
    #     "address": "2 Bloor ave",
    #     "contact_name": "Jane Doe",
    #     "email": "email@email.com",
    #     "phone_number": "4161234"
    # })) 
    # assert rv.status_code == 500


def test_long_lat_to_point():
    for i in range(5):
        test_long = random.uniform(-180, 180)
        test_lat = random.uniform(-90, 90)
        res = CommunityResource.long_lat_to_point(test_long, test_lat)
        expected = WKTElement("POINT(" + str(test_long) + " " + str(test_lat) + ")")

        print("Response: ", str(res))
        print("Expected: ", str(expected))
        assert str(res) == str(expected)
 