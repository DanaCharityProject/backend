from unittest.mock import patch

import pytest

from app import models


@patch("flask_sqlalchemy.SignallingSession", autospec=True)
def test_user(mock_session):
    username = "foo"
    password = "bar"

    user = models.User(id=1, username=username)

    user.password = password

    assert user.verify_password(password)
    assert not user.verify_password("baz")

    with pytest.raises(AttributeError):
        print(user.password)

    assert user.to_dict() == {
        "id": 1,
        "username": user.username
    }
