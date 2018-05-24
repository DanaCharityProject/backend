import pytest
from unittest.mock import patch

from app import create_app
from app.auth import auth


@pytest.mark.skip()
@patch("app.auth.current_role")
def test_rbac_access(current_role):
    assert False
