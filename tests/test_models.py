from unittest.mock import patch

import pytest

from app import user_model, user_manager_model, community_resource_model, exception_models


@patch("flask_sqlalchemy.SignallingSession", autospec=True)
def test_user_password(mock_session):
    username = "foo"
    password = "bar"

    user = user_model.User(id=1, username=username)

    user.password = password

    # correct password
    assert user.verify_password(password)

    # incorrect password
    assert not user.verify_password("baz")

    # password is write-only
    with pytest.raises(AttributeError):
        print(user.password)


@patch("app.user_model.db.Model.query")
@patch("app.user_model.current_app")
@patch("flask_sqlalchemy.SignallingSession", autospec=True)
def test_user_token(mock_session, mock_current_app, mock_query):
    username = "foo"
    password = "bar"
    user = user_model.User(id=1, username=username)
    user.password = password

    mock_current_app.config = {"SECRET_KEY": "secret-key"}
    mock_query.get = {user.id: user}.get

    token = user.generate_auth_token()

    user_ = user_model.User.verify_auth_token(token)

    # correct token
    assert user == user_

    user_ = user_model.User.verify_auth_token("afdlkjsls;kfd")

    # incorrect token
    assert user_ is None

    token = user.generate_auth_token(expiration=-1)
    user_ = user_model.User.verify_auth_token(token)

    # expired token
    assert user_ is None

    mock_current_app.config = {"SECRET_KEY": "secret-key2"}
    user_ = user_model.User.verify_auth_token(token)

    # different key
    assert user_ is None
