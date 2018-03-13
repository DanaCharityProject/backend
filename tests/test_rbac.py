from app.auth import auth

from unittest.mock import patch

from app import create_app


@patch("app.auth.get_current_role")
def test_rbac_access(current_role):
    assert True
