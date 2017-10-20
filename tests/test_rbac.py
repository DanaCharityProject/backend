from app.models.rbac import AdminRole, UserRole, CommunityResourceRole
from app.auth import accept_roles

from unittest.mock import patch

from app import create_app


@patch("app.auth.get_current_role")
def test_rbac_access(current_role):

    @accept_roles([AdminRole])
    def foo():
        return 200

    current_role.return_value = AdminRole()

    assert foo() == 200

    current_role.return_value = UserRole()

    assert foo() == None
