import pytest

from typing import Tuple
from django.contrib.auth.models import User, AbstractUser
from odevlib.business_logic.rbac.permissions import (
    get_complete_roles_permissions,
    get_complete_user_roles,
    get_instance_user_roles,
    get_roles_permissions,
    get_user_roles,
)

from odevlib.models.rbac.role import RBACRole
from odevlib.models.rbac.role_assignment import RoleAssignment
from odevlib.models.rbac.instance_role_assignment import InstanceRoleAssignment


### TESTS ###


@pytest.mark.django_db
def test_rbac_permission_inheritance(superuser: AbstractUser, rbac_child_role: Tuple[RBACRole, RBACRole]) -> None:
    """
    Test that a parent role inherits all permissions from its children.
    Keep in mind that "parent" includes all "children" permissions, not the other way around.
    """
    parent, child = rbac_child_role

    # Add permission to child
    child.permissions["test_permission"] = "rwd"
    child.save(user=superuser)

    # Check that permissions appeared in the parent
    permissions = get_complete_roles_permissions([parent])
    assert "test_permission" in permissions
    assert set(permissions["test_permission"]) == set("rwd")


@pytest.mark.django_db
def test_rbac_permission_inheritance_addition(
    superuser: AbstractUser, rbac_child_role: Tuple[RBACRole, RBACRole]
) -> None:
    """
    Test that a parent role can add permissions from its child.
    """
    parent, child = rbac_child_role

    # Add permission to parent
    parent.permissions["test_permission"] = "r"
    parent.save(user=superuser)

    # Add permission in child
    child.permissions["test_permission"] = "wd"
    child.save(user=superuser)

    permissions = get_complete_roles_permissions([parent])
    assert "test_permission" in permissions
    assert set(permissions["test_permission"]) == set("rwd")


@pytest.mark.django_db
def test_rbac_permission_no_reverse_inheritance(
    superuser: AbstractUser, rbac_child_role: Tuple[RBACRole, RBACRole]
) -> None:
    """
    Test that a child role does not inherit permissions from its parent.
    """
    parent, child = rbac_child_role

    # Add permission to parent
    parent.permissions["test_permission"] = "rwd"
    parent.save(user=superuser)

    # Check that permissions did not appear in the child
    permissions = get_complete_roles_permissions([child])
    assert "test_permission" not in permissions


@pytest.mark.django_db
def test_role_direct_assignment(superuser: AbstractUser, user: AbstractUser, rbac_role: RBACRole) -> None:
    """
    Test that a user can be assigned a role.
    """
    # Assign role to user
    assert isinstance(user, User)
    rbac_role.permissions["test_permission"] = "rwd"
    rbac_role.save(user=superuser)
    assignment = RoleAssignment(role=rbac_role, user=user)
    assignment.save(user=superuser)

    # Check that user has the permission
    roles = get_user_roles(user)
    permissions = get_roles_permissions(roles)

    assert "test_permission" in permissions
    assert set(permissions["test_permission"]) == set("rwd")


@pytest.mark.django_db
def test_role_inherited_assignment(
    superuser: AbstractUser, user: AbstractUser, rbac_child_role: Tuple[RBACRole, RBACRole]
) -> None:
    """
    Test that a user has permissions that are stored in a role that is inherited from a direct role.
    """
    parent, child = rbac_child_role

    # Assign role to user
    assert isinstance(user, User)
    child.permissions["test_permission"] = "rwd"
    child.save(user=superuser)
    assignment = RoleAssignment(role=parent, user=user)
    assignment.save(user=superuser)

    # Check that user has the permission
    roles = get_complete_user_roles(user)
    permissions = get_roles_permissions(roles)

    assert "test_permission" in permissions
    assert set(permissions["test_permission"]) == set("rwd")


@pytest.mark.django_db
def test_direct_instance_role_assignment(superuser: AbstractUser, user: AbstractUser, rbac_role: RBACRole) -> None:
    """
    Test that a user can be assigned a direct role to an instance.
    """
    # Assign role to user
    assert isinstance(user, User)
    rbac_role.permissions["test_permission"] = "rwd"
    rbac_role.save(user=superuser)
    assignment = InstanceRoleAssignment(role=rbac_role, user=user, model="odevlib__rbacrole", instance_id=rbac_role.pk)
    assignment.save(user=superuser)

    # Check that user has the permission
    roles = get_instance_user_roles(user, model=RBACRole, instance_id=rbac_role.pk)
    permissions = get_roles_permissions(roles)

    assert "test_permission" in permissions
    assert set(permissions["test_permission"]) == set("rwd")


@pytest.mark.django_db
def test_direct_instance_role_assignment_does_not_leak_into_other_instances(
    superuser: AbstractUser, user: AbstractUser, rbac_role: RBACRole
) -> None:
    """
    Test that a user can be assigned a direct role to an instance, and that the role does not leak into other instances.
    """
    # Assign role to user
    assert isinstance(user, User)
    rbac_role.permissions["test_permission"] = "rwd"
    rbac_role.save(user=superuser)
    assignment = InstanceRoleAssignment(role=rbac_role, user=user, model="odevlib__rbacrole", instance_id=rbac_role.pk)
    assignment.save(user=superuser)

    # Check that user has the permission
    roles = get_instance_user_roles(user, model=RBACRole, instance_id=rbac_role.pk + 1)
    permissions = get_roles_permissions(roles)

    assert "test_permission" not in permissions


@pytest.mark.django_db
def test_direct_instance_role_assignment_does_not_leak_into_global_assignments(
    superuser: AbstractUser, user: AbstractUser, rbac_role: RBACRole
) -> None:
    """
    Test that a user can be assigned a direct role to an instance, and that the role does not leak into global assignments.
    """
    # Assign role to user
    assert isinstance(user, User)
    rbac_role.permissions["test_permission"] = "rwd"
    rbac_role.save(user=superuser)
    assignment = InstanceRoleAssignment(role=rbac_role, user=user, model="odevlib__rbacrole", instance_id=rbac_role.pk)
    assignment.save(user=superuser)

    # Check that user has the permission
    roles = get_complete_user_roles(user)
    permissions = get_roles_permissions(roles)

    assert "test_permission" not in permissions
