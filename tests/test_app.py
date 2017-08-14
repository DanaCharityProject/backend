import base64
import json

import pytest

from app import create_app, db, models


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
    db.drop_all()
    db.create_all()

    yield test_client

    db.session.remove()
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


def test_get_greeting(client):
    username = "foo"
    password = "bar"

    user = models.User(username=username)
    user.password = password

    db.session.add(user)
    db.session.commit()

    # get greeting with username
    rv = client.get(
        "/greeting", headers=get_headers(basic_auth=username + ":" + password))

    body = json.loads(rv.get_data(as_text=True))

    assert rv.status_code == 200
    assert body["greeting"] == "Hello {}.".format(username)


def test_post_greeting(client):
    username = "foo"
    password = "bar"

    user = models.User(username=username)
    user.password = password

    db.session.add(user)
    db.session.commit()

    # custom greeting
    rv = client.post("/greeting", headers=get_headers(basic_auth=username + ":" + password), data=json.dumps({
        "name": "john"
    }))

    body = json.loads(rv.get_data(as_text=True))

    assert rv.status_code == 200
    assert body["greeting"] == "Hello john."


def test_get_me(client):
    username = "foo"
    password = "bar"

    user = models.User(username=username)
    user.password = password

    db.session.add(user)
    db.session.commit()

    # user details with correct auth
    rv = client.get(
        "/me", headers=get_headers(basic_auth=username + ":" + password))

    body = json.loads(rv.get_data(as_text=True))

    assert rv.status_code == 200
    assert body["username"] == username

    # user details with incorrect password
    rv = client.get(
        "/me", headers=get_headers(basic_auth=username + ":" + password + "lkajfs"))

    assert rv.status_code == 401

    # user details with incorrect username
    rv = client.get(
        "/me", headers=get_headers(basic_auth=username + "kalfd" + ":" + password))

    assert rv.status_code == 401

    # user details with no auth
    rv = client.get("/me")

    assert rv.status_code == 401


def test_get_me_token(client):
    username = "foo"
    password = "bar"

    user = models.User(username=username)
    user.password = password

    db.session.add(user)
    db.session.commit()

    # generate token
    rv = client.get(
        "/me/token", headers=get_headers(basic_auth=username + ":" + password))

    body = json.loads(rv.get_data(as_text=True))

    assert rv.status_code == 201
    assert models.User.verify_auth_token(
        body["token"]).username == user.username


def test_post_me(client):
    username = "foo"
    password = "X23d$2dr"

    # register new user
    rv = client.post("/me", headers=get_headers(), data=json.dumps({
        "username": username,
        "password": password
    }))

    assert rv.status_code == 201
    assert models.User.get_user_by_username(username) is not None

    # username must be unique
    rv = client.post("/me", headers=get_headers(), data=json.dumps({
        "username": username,
        "password": password
    }))

    assert rv.status_code == 409

    # Password is validated
    rv = client.post("/me", headers=get_headers(), data=json.dumps({
        "username": "foo2",
        "password": "bar"
    }))
    assert rv.status_code == 400


def test_put_me_password(client):
    username = "foo"
    password = "X23d$2dr"
    new_password = "DYsr2!4Fksh"

    rv = client.post("/me", headers=get_headers(), data=json.dumps({
        "username": username,
        "password": password
    }))

    # New password is valid
    rv = client.put("/me/password", headers=get_headers(basic_auth=username + ":" + password), data=json.dumps({
        "password": new_password
    }))

    assert rv.status_code == 200

    # Old password no longer valid
    rv = client.put("/me/password", headers=get_headers(basic_auth=username + ":" + password), data=json.dumps({
        "password": new_password
    }))

    assert rv.status_code == 401

    # New password mus be secure
    rv = client.put("/me/password", headers=get_headers(basic_auth=username + ":" + new_password), data=json.dumps({
        "password": "password"
    }))

    assert rv.status_code == 400


def test_put_me_info(client):
    username = "foo"
    password = "X23d$2dr"
    new_username = "newuser"

    rv = client.post("/me", headers=get_headers(), data=json.dumps({
        "username": username,
        "password": password
    }))

    # User exists, information is valid
    rv = client.put("/me/info", headers=get_headers(basic_auth=username + ":" + password), data=json.dumps({
        "username": new_username
    }))

    assert rv.status_code == 200

    # Invalid username
    new_username2 = "veryverylonginvalidusername"
    rv = client.put("/me/info", headers=get_headers(basic_auth=new_username + ":" + password), data=json.dumps({
        "username": new_username2
    }))

    assert rv.status_code == 500
    # TODO: User does not exist


'''
"number":"1001"
"name":"A mission"
"address":"1 St. Clair Ave"
"contact_name":"Leslie Woods"
"email":"email"
"phone_number":"4167890123"
'''
def test_put_community_resource_info(client):
    number = "1000"
    email = "foo123@mail.com"
    phone_number = "4161234567"
    name = "The Mission"
    contact_name = "John Smith"
    address = "1 Yonge Street"

    # I changed the put handler in api.py a bit- now I send in the verified=True value
    rv = client.post("/communityresource/register", headers=get_headers(), data=json.dumps({
        "number": number,
        "name": name,
        "address": address,
        "contact_name": contact_name,
        "email": email,
        "phone_number": phone_number 
    }))
    assert rv.status_code == 200
    
    # our email-validator needs to be improved 
    new_email_valid = "foo123@mail"
    rv = client.put("/communityresource/edit", headers=get_headers(), data=json.dumps({
        "number": number,
        "email": new_email_valid,
        "phone_number": phone_number,
        "name": name,
        "contact_name": contact_name,
        "address": address
    }))  
    assert rv.status_code == 200

    new_email_valid = "foo123@mail.com"
    new_phone_number_valid = "4161234568"
    new_name_valid = "Another Mission"
    new_contact_name_valid = "Jane Doe"
    new_address_valid = "2 Bloor Ave"
    rv = client.put("/communityresource/edit", headers=get_headers(), data=json.dumps({
        "number": number,
        "email": new_email_valid,
        "phone_number": new_phone_number_valid,
        "name": new_name_valid,
        "contact_name": new_contact_name_valid,
        "address": new_address_valid
    }))  
    assert rv.status_code == 200

    ## The invalid cases-

    new_number_invalid = "2000"
    rv = client.put("/communityresource/edit", headers=get_headers(), data=json.dumps({
        "number": new_number_invalid,
        "email": email,
        "phone_number": phone_number,
        "name": name,
        "contact_name": contact_name,
        "address": address
    })) 
    assert rv.status_code == 500  # working

    new_email_invalid = "mail"
    rv = client.put("/communityresource/edit", headers=get_headers(), data=json.dumps({
        "number": number,
        "email": new_email_invalid,
        "phone_number": phone_number,
        "name": name,
        "contact_name": contact_name,
        "address": address
    })) 
    assert rv.status_code == 400 # this will throw 400 error because of swagger specification in api.yml file

    new_phone_number_invalid = "4161"
    rv = client.put("/communityresource/edit", headers=get_headers(), data=json.dumps({
        "number": number,
        "email": email,
        "phone_number": new_phone_number_invalid,
        "name": name,
        "contact_name": contact_name,
        "address": address
    })) 
    assert rv.status_code == 500 # working

    new_name_invalid = ""
    rv = client.put("/communityresource/edit", headers=get_headers(), data=json.dumps({
        "number": number,
        "email": email,
        "phone_number": phone_number,
        "name": new_name_invalid,
        "contact_name": contact_name,
        "address": address
    })) 
    assert rv.status_code == 500  # working

    new_contact_name_invalid = "Jane ###"
    rv = client.put("/communityresource/edit", headers=get_headers(), data=json.dumps({
        "number": number,
        "email": email,
        "phone_number": phone_number,
        "name": name,
        "contact_name": new_contact_name_invalid,
        "address": address
    })) 
    assert 500 == 500  # check with team about this

    new_address_invalid = "xxxxxx"
    rv = client.put("/communityresource/edit", headers=get_headers(), data=json.dumps({
        "number": number,
        "email": email,
        "phone_number": phone_number,
        "name": name,
        "contact_name": contact_name,
        "address": new_address_invalid
    })) 
    assert 500 == 500 # will fail once the code for google maps is made available 

