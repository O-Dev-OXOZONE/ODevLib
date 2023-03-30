from typing import Tuple
from pytest import fixture

from django.contrib.auth.models import User, AbstractUser

from odevlib.models.rbac.role_hierarchy import RoleHierarchyEntry
from odevlib.models.rbac.role import RBACRole
from odevlib.models.simple_permission_system import SimplePermissionSystemPermission


@fixture
def rbac_role(superuser: AbstractUser, name="test_role") -> RBACRole:
    role = RBACRole(name=name, permissions={})
    role.save(user=superuser)
    return role


@fixture
def rbac_child_role(superuser: AbstractUser, rbac_role: RBACRole, name="test_child_role") -> Tuple[RBACRole, RBACRole]:
    """
    Creates a parent role and a child role and returns both.
    """
    child = RBACRole(name=name, permissions={})
    child.save(user=superuser)
    entry = RoleHierarchyEntry(parent_role=rbac_role, child_role=child)
    entry.save(user=superuser)
    return rbac_role, child


@fixture
def rbac_simple_permission() -> SimplePermissionSystemPermission:
    permission = SimplePermissionSystemPermission(
        subsystem="rbac",
        name="RBAC full access",
        can_create=True,
        can_read=True,
        can_update=True,
        can_delete=True,
    )
    permission.save()
    return permission

