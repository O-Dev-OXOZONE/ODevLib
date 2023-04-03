import pytest
from django.contrib.auth.models import AbstractUser, User
from rest_framework.test import APIClient
from odevlib.business_logic.rbac.permissions import get_roles_permissions, get_user_roles

from odevlib.models.rbac.role import RBACRole
from odevlib.models.rbac.role_assignment import RoleAssignment
from odevlib.models.simple_permission_system import SimplePermissionAssignment, SimplePermissionSystemPermission


@pytest.mark.django_db
def test_serializer_field_filtering_for_retrieve(
    superuser: AbstractUser,
    user: AbstractUser,
    rbac_role: RBACRole,
    authorized_api_client: APIClient,
    rbac_simple_permission: SimplePermissionSystemPermission,
):
    """
    Test that a user can only see the fields that he has access to, given the global role assignment.
    """
    # Assign role to user
    assert isinstance(user, User)
    rbac_role.permissions["odevlib__rbacrole__name"] = "r"
    rbac_role.save(user=superuser)
    sps_assignment = SimplePermissionAssignment(permission=rbac_simple_permission, user=user)
    sps_assignment.save(user=superuser)
    assignment = RoleAssignment(role=rbac_role, user=user)
    assignment.save(user=superuser)

    response = authorized_api_client.get(f"/odl/rbacrole/{rbac_role.pk}/")

    assert response.json() == {
        "id": rbac_role.pk,
        "name": rbac_role.name,
    }
