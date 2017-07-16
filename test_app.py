import app
from app import create_app
import pytest
import json


@pytest.fixture
def client():
    app = create_app("testing")
    flaskapp = app.app

    test_client = flaskapp.test_client()

    ctx = flaskapp.app_context()
    ctx.push()

    yield test_client

    ctx.pop()

def test_post_greeting(client):
    rv = client.post("/greeting", headers={"Content-type": "application/json"}, data=json.dumps({
        "name": "john"
    }))

    assert rv.status_code == 200
    assert "Hello john." in rv.get_data(as_text=True)