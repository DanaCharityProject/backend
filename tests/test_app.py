import base64
import json

import pytest

from app import create_app, db, models


@pytest.fixture
def client():
    app = create_app("testing")
    flaskapp = app.app

    test_client = flaskapp.test_client()

    ctx = flaskapp.app_context()
    ctx.push()

    db.create_all()

    yield test_client

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

    rv = client.get(
        "/greeting", headers=get_headers(basic_auth=username + ":" + password))

    assert rv.status_code == 200
    assert "Hello {}.".format(username) in rv.get_data(as_text=True)


def test_post_greeting(client):
    username = "foo"
    password = "bar"

    user = models.User(username=username)
    user.password = password

    db.session.add(user)
    db.session.commit()

    rv = client.post("/greeting", headers=get_headers(basic_auth=username + ":" + password), data=json.dumps({
        "name": "john"
    }))

    assert rv.status_code == 200
    assert "Hello john." in rv.get_data(as_text=True)


def test_get_me(client):
    username = "foo"
    password = "bar"

    user = models.User(username=username)
    user.password = password

    db.session.add(user)
    db.session.commit()

    rv = client.get(
        "/me", headers=get_headers(basic_auth=username + ":" + password))

    body = json.loads(rv.get_data(as_text=True))

    assert rv.status_code == 200
    assert body["username"] == username


def test_post_me(client):
    username = "foo"
    password = "bar"

    rv = client.post("/me", headers=get_headers(), data=json.dumps({
        "username": username,
        "password": password
    }))

    assert rv.status_code == 201
