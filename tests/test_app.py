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
    password = "bar"

    # register new user
    rv = client.post("/me", headers=get_headers(), data=json.dumps({
        "username": username,
        "password": password
    }))

    db.session.remove()

    assert rv.status_code == 201
