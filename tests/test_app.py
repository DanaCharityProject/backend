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


def test_get_user(client):
    username = "foo"
    password = "bar"

    user = models.User(username=username)
    user.password = password

    db.session.add(user)
    db.session.commit()

    # user details with correct auth
    rv = client.get(
        "/user", headers=get_headers(basic_auth=username + ":" + password))

    body = json.loads(rv.get_data(as_text=True))

    assert rv.status_code == 200
    assert body["username"] == username

    # user details with incorrect password
    rv = client.get(
        "/user", headers=get_headers(basic_auth=username + ":" + password + "lkajfs"))

    assert rv.status_code == 401

    # user details with incorrect username
    rv = client.get(
        "/user", headers=get_headers(basic_auth=username + "kalfd" + ":" + password))

    assert rv.status_code == 401

    # user details with no auth
    rv = client.get("/user")

    assert rv.status_code == 401


def test_get_user_token(client):
    username = "foo"
    password = "bar"

    user = models.User(username=username)
    user.password = password

    db.session.add(user)
    db.session.commit()

    # generate token
    rv = client.get(
        "/user/token", headers=get_headers(basic_auth=username + ":" + password))

    body = json.loads(rv.get_data(as_text=True))

    assert rv.status_code == 201
    assert models.User.verify_auth_token(
        body["token"]).username == user.username


def test_post_user(client):
    username = "foo"
    password = "X23d$2dr"

    # register new user
    rv = client.post("/user", headers=get_headers(), data=json.dumps({
        "username": username,
        "password": password
    }))

    assert rv.status_code == 201
    assert models.User.get_user_by_username(username) is not None

    # username must be unique
    rv = client.post("/user", headers=get_headers(), data=json.dumps({
        "username": username,
        "password": password
    }))

    assert rv.status_code == 409

    # Password is validated
    rv = client.post("/user", headers=get_headers(), data=json.dumps({
        "username": "foo2",
        "password": "bar"
    }))
    assert rv.status_code == 400


def test_put_user_password(client):
    username = "foo"
    password = "X23d$2dr"
    new_password = "DYsr2!4Fksh"

    rv = client.post("/user", headers=get_headers(), data=json.dumps({
        "username": username,
        "password": password
    }))

    # New password is valid
    rv = client.put("/user/password", headers=get_headers(basic_auth=username + ":" + password), data=json.dumps({
        "password": new_password
    }))

    assert rv.status_code == 200

    # Old password no longer valid
    rv = client.put("/user/password", headers=get_headers(basic_auth=username + ":" + password), data=json.dumps({
        "password": new_password
    }))

    assert rv.status_code == 401

    # New password mus be secure
    rv = client.put("/user/password", headers=get_headers(basic_auth=username + ":" + new_password), data=json.dumps({
        "password": "password"
    }))

    assert rv.status_code == 400


def test_put_user_info(client):
    username = "foo"
    password = "X23d$2dr"
    new_username = "newuser"

    rv = client.post("/user", headers=get_headers(), data=json.dumps({
        "username": username,
        "password": password
    }))

    # User exists, information is valid
    rv = client.put("/user/info", headers=get_headers(basic_auth=username + ":" + password), data=json.dumps({
        "username": new_username
    }))

    assert rv.status_code == 200

    # Invalid username
    new_username2 = "veryverylonginvalidusername"
    rv = client.put("/user/info", headers=get_headers(basic_auth=new_username + ":" + password), data=json.dumps({
        "username": new_username2
    }))

    assert rv.status_code == 500

    # TODO: User does not exist

