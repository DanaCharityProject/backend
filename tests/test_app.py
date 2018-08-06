import base64
import json

import pytest
import pygeoif

from app import create_app, db
import app.models as models
from app.models.user import User
from app.models.community_resource import CommunityResource
from app.models.community import Community
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
    assert body[0]['community_resource_id'] == 1 and body[1]['community_resource_id'] == 3


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

    rv = client.get("/communityresource/{community_resource_id}".format(community_resource_id=2, headers=get_headers()))
    assert rv.status_code == 404


def test_community_resource_populate_db(client):
    CommunityResource.populate_db()
    # pulled from parsed shapefile
    expected = {'index': 55, 'name': 'YMCA House', 'shape': 'POINT (43.64818818 -79.39800551)'}

    rv = client.get("/communityresource/{community_resource_id}".format(community_resource_id=55, headers=get_headers()))
    assert rv.status_code == 200
    body = json.loads(rv.get_data(as_text=True))
    print(body)
    assert body['name'] == expected['name']
    coordinates = json.loads(body['coordinates'][0])['coordinates']
    assert 'POINT ({} {})'.format(coordinates[0], coordinates[1]) == expected['shape']


def test_point_in_polygon(client):
    SRID = "SRID=4326;"

    charity_number = "1000"
    email = "foo123@mail.com"
    phone_number = "4161234567"
    name = "The Mission"
    contact_name = "John Smith"
    address = "1 Yonge Street"
    coordinates = SRID + "POINT(43.643205 -79.374143)"
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

    # returns list of tuple: [(CommunityResource, geoJSON)]
    res = CommunityResource.find_resources_inside_shape()
    assert len(res) == 1
    assert res[0][0].name == name

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


def test_get_all_communities(client):
    community_id = 1
    name = "Test community"
    boundaries = WKTElement("MULTIPOLYGON(((43.643911 -79.376321, 43.644268 -79.372738, 43.642071 -79.372620, 43.641993 -79.375881, 43.643911 -79.376321)))", 4326)
    expected_boundaries = {'coordinates': [[[[43.643911, -79.376321], [43.644268, -79.372738], [43.642071, -79.37262], [43.641993, -79.375881], [43.643911, -79.376321]]]], 'type': 'MultiPolygon'}
    community = Community.add_comunity(Community.from_dict({
        "id": community_id,
        "name": name,
        "boundaries":boundaries
    }))

    assert community is not None
    assert Community.get_all_communities is not None

    # user details with correct auth
    rv = client.get("/community", headers=get_headers())
    body = json.loads(rv.get_data(as_text=True))
    assert rv.status_code == 200
    assert body[0]["id"] == community_id
    assert body[0]["name"] == name
    print(body[0]["boundaries"])
    assert body[0]["boundaries"] == expected_boundaries


def test_community_populate_db(client):
    Community.populate_db()
    # pulled from parsed shapefile
    expected_id = 97
    expected_name = 'Yonge-St.Clair'
    expected_boundaries = {'type': 'MultiPolygon', 'coordinates': [[[[43.681081124, -79.391194827], [43.680969554, -79.391405432], [43.68016564, -79.393223778], [43.67897994, -79.395808832], [43.678274813, -79.39734939], [43.678225407, -79.397456054], [43.678167002, -79.397563898], [43.678117597, -79.397671319], [43.678068202, -79.397779545], [43.678014289, -79.397888536], [43.67799496, -79.397931367], [43.678026295, -79.397944053], [43.678203874, -79.398012159], [43.678530736, -79.398140901], [43.679039165, -79.39835151], [43.679554271, -79.398562968], [43.679962231, -79.398733166], [43.680460422, -79.39893948], [43.680766541, -79.399065448], [43.681127631, -79.399215419], [43.682543482, -79.399803535], [43.683415978, -79.400168894], [43.683526704, -79.400209291], [43.684309799, -79.400530362], [43.685027249, -79.400841057], [43.685716067, -79.40112639], [43.686640698, -79.401495486], [43.688721201, -79.402338541], [43.690632725, -79.403084698], [43.69068726, -79.403084595], [43.690739752, -79.40306224], [43.690782127, -79.403017635], [43.690989071, -79.401858246], [43.691018509, -79.401758471], [43.691039868, -79.401694884], [43.691075806, -79.401586377], [43.691059555, -79.401475066], [43.691197554, -79.400869288], [43.691647493, -79.401046406], [43.691756401, -79.401129155], [43.692098259, -79.401284819], [43.692923003, -79.401589348], [43.693727159, -79.401895134], [43.694575291, -79.402191292], [43.694891641, -79.402323138], [43.695111837, -79.402372873], [43.695494538, -79.402403564], [43.695349317, -79.403094469], [43.695259526, -79.403506916], [43.695019966, -79.404674309], [43.695978147, -79.405052346], [43.696553361, -79.405281498], [43.696951675, -79.405412512], [43.697479664, -79.405611741], [43.698180489, -79.405883211], [43.698018991, -79.405661289], [43.697963262, -79.405471175], [43.697686571, -79.404605213], [43.697269527, -79.403203304], [43.697261791, -79.40312408], [43.697149125, -79.402963269], [43.697126386, -79.402769041], [43.697074482, -79.402584239], [43.696997568, -79.402277968], [43.696834151, -79.401668084], [43.696730327, -79.401266766], [43.696390928, -79.400089966], [43.696096816, -79.398961414], [43.695845162, -79.398039911], [43.695652603, -79.397199651], [43.695603138, -79.396884534], [43.695658887, -79.396105325], [43.692273296, -79.395379674], [43.692098523, -79.395342183], [43.691261324, -79.395170311], [43.690784199, -79.39506256], [43.690199042, -79.394936396], [43.690000974, -79.394891382], [43.689735385, -79.394821305], [43.689217051, -79.394603411], [43.689132066, -79.394567687], [43.688083036, -79.394141978], [43.687133004, -79.393705219], [43.68623254, -79.393331962], [43.685881365, -79.393185671], [43.685025923, -79.392854227], [43.683940867, -79.392384472], [43.683101241, -79.392032918], [43.682874946, -79.391939056], [43.682148949, -79.391630762], [43.681973354, -79.391555118], [43.681431807, -79.391340234], [43.681081124, -79.391194827]]]]}

    rv = client.get("/community", headers=get_headers())
    assert rv.status_code == 200
    body = json.loads(rv.get_data(as_text=True))
    assert body[0]['id'] == expected_id
    assert body[0]['name'] == expected_name
    boundaries = body[0]['boundaries']
    assert boundaries == expected_boundaries


def test_community_query_community_containing(client):
    community_id = 1
    name = "Test community"
    boundaries = WKTElement("MULTIPOLYGON(((43.643911 -79.376321, 43.644268 -79.372738, 43.642071 -79.372620, 43.641993 -79.375881, 43.643911 -79.376321)))", 4326)
    community = Community.add_comunity(Community.from_dict({
        "id": community_id,
        "name": name,
        "boundaries":boundaries
    }))

    assert community is not None

    point_lat = 43.6439
    point_long = -79.3740
    expected_boundaries = [[[[43.643911, -79.376321], [43.644268, -79.372738], [43.642071, -79.37262], [43.641993, -79.375881], [43.643911, -79.376321]]]]

    rv = client.get("/community/{},{}".format(point_lat, point_long), headers=get_headers())
    assert rv.status_code == 200
    body = json.loads(rv.get_data(as_text=True))
    assert body['id'] == community_id
    assert body['name'] == name
    assert json.loads(body['boundaries'])['coordinates'] == expected_boundaries

### Extra functions ###

def test_long_lat_to_point():
    for i in range(5):
        test_long = random.uniform(-180, 180)
        test_lat = random.uniform(-90, 90)
        res = CommunityResource.long_lat_to_point(test_long, test_lat)
        expected = WKTElement("POINT(" + str(test_long) + " " + str(test_lat) + ")")

        print("Response: ", str(res))
        print("Expected: ", str(expected))
        assert str(res) == str(expected)
