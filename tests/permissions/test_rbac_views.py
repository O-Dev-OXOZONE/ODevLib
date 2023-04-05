from django.contrib.auth.models import User
from django.urls import reverse
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from odevlib.models.rbac.instance_role_assignment import InstanceRoleAssignment

from odevlib.models.rbac.role import RBACRole
from odevlib.models.rbac.role_assignment import RoleAssignment


@pytest.mark.django_db
def test_do_i_have_rbac_permission_global(
    authorized_api_client: APIClient,
    superuser: User,
    user: User,
    rbac_role: RBACRole,
):
    """
    Test that a user can check if they have a global permission.
    """
    rbac_role.permissions["test_permission"] = "cr"
    rbac_role.save(user=superuser)
    rbac_role_assignment = RoleAssignment(user=user, role=rbac_role)
    rbac_role_assignment.save(user=superuser)

    response = authorized_api_client.get(
        "/odl/do_i_have_rbac_permission/?permission=test_permission",
    )

    assert response.status_code == status.HTTP_200_OK
    assert set(response.data) == set("cr")


@pytest.mark.django_db
def test_do_i_have_rbac_permission_fail(
    authorized_api_client: APIClient,
    superuser: User,
    user: User,
    rbac_role: RBACRole,
):
    """
    Test that permissions do not leak when executing do_i_have_rbac_permission.
    """
    rbac_role.permissions["test_permission"] = "cr"
    rbac_role.save(user=superuser)
    rbac_role_assignment = RoleAssignment(user=user, role=rbac_role)
    rbac_role_assignment.save(user=superuser)

    response = authorized_api_client.get(
        "/odl/do_i_have_rbac_permission/?permission=test_permission_1",
    )

    assert response.status_code == status.HTTP_200_OK
    assert set(response.data) == set("None")


@pytest.mark.django_db
def test_get_my_roles_and_permissions_global(
    authorized_api_client: APIClient,
    superuser: User,
    user: User,
    rbac_role: RBACRole,
):
    """
    Test that a user can get their global permissions.
    """
    rbac_role.permissions["test_permission"] = "cr"
    rbac_role.save(user=superuser)
    rbac_role_assignment = RoleAssignment(user=user, role=rbac_role)
    rbac_role_assignment.save(user=superuser)

    response = authorized_api_client.get("/odl/get_my_roles_and_permissions/")

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "roles": [
            rbac_role.name,
        ],
        "permissions": {
            "test_permission": "".join(list(set("cr"))),
        },
    }


@pytest.mark.django_db
def test_get_my_roles_and_permissions_instance_level(
    authorized_api_client: APIClient,
    superuser: User,
    user: User,
    rbac_role: RBACRole,
):
    """
    Test that a user can get their instance level permissions.
    """
    rbac_role.permissions["odevlib__rbacrole__name"] = "cr"
    rbac_role.save(user=superuser)
    rbac_role_assignment = InstanceRoleAssignment(
        user=user, role=rbac_role, model="odevlib__rbacrole", instance_id=rbac_role.pk
    )
    rbac_role_assignment.save(user=superuser)

    response = authorized_api_client.get(
        f"/odl/get_my_roles_and_permissions/?model_name=odevlib__rbacrole&instance_id={rbac_role.pk}",
    )

    assert response.status_code == status.HTTP_200_OK, f"Got non-200 status code with body: {response.data}"
    assert response.data == {
        "roles": [
            rbac_role.name,
        ],
        "permissions": {
            "odevlib__rbacrole__name": "".join(list(set("cr"))),
        },
    }


@pytest.mark.django_db
def test_get_my_roles_and_permissions_instance_level_dont_leak_to_global(
    authorized_api_client: APIClient,
    superuser: User,
    user: User,
    rbac_role: RBACRole,
):
    """
    Test that a user can get their instance level permissions.
    """
    rbac_role.permissions["odevlib__rbacrole__name"] = "cr"
    rbac_role.save(user=superuser)
    rbac_role_assignment = InstanceRoleAssignment(
        user=user, role=rbac_role, model="odevlib__rbacrole", instance_id=rbac_role.pk
    )
    rbac_role_assignment.save(user=superuser)

    response = authorized_api_client.get(
        f"/odl/get_my_roles_and_permissions/",
    )

    assert response.status_code == status.HTTP_200_OK, f"Got non-200 status code with body: {response.data}"
    assert response.data == {
        "roles": [],
        "permissions": {},
    }
