import itertools
import logging
from collections import defaultdict
from collections.abc import Iterable, Mapping

from django.contrib.auth.models import AbstractUser
from django.db import models

from odevlib.errors import codes
from odevlib.models import RBACRole
from odevlib.models.errors import Error
from odevlib.models.rbac.instance_role_assignment import InstanceRoleAssignment
from odevlib.models.rbac.mixins import RBACHierarchyModelMixin
from odevlib.utils.functional import flatten

create_methods = ["POST"]
"""
HTTP methods that use 'c' access mode.
"""

read_methods = ["GET", "OPTIONS", "HEAD"]
"""
HTTP methods that use 'r' access mode.
"""

write_methods = ["PUT", "PATCH"]
"""
HTTP methods that use 'u' access mode.
"""

delete_methods = ["DELETE"]
"""
HTTP methods that use 'd' access mode.
"""


def get_direct_rbac_roles(user: AbstractUser) -> Iterable[RBACRole]:
    """
    Return all roles directly assigned to a user.
    Result does NOT include inherited roles.

    This function is the root for getting roles, as its implementation may change to include
    caching, other databases, etc.
    """
    return RBACRole.objects.for_user(user)


def get_complete_rbac_roles(user: AbstractUser) -> Iterable[RBACRole]:
    """
    Return all roles assigned to a user, recursively following children.

    This function is the root for getting roles, as its implementation may change to include
    caching, other databases, etc.

    Current implementation falls back to the ORM selects, and is very inefficient.

    TODO: introduce caching
    """
    roles = get_direct_rbac_roles(user)

    def recurse(role: RBACRole) -> Iterable[RBACRole]:
        yield role
        for child in RBACRole.objects.children_of(role):
            yield from recurse(child)

    # Merge multiple iterables into one
    return itertools.chain.from_iterable(recurse(role) for role in roles)


def get_roles_permissions(roles: Iterable[RBACRole]) -> Mapping[str, str]:
    """
    Return a mapping of permissions to access modes for a given set of roles.
    """

    assert isinstance(roles, Iterable), "get_roles_permissions(): roles must be an iterable"

    return merge_permissions(list(roles))


def collect_role_children(role: RBACRole) -> Iterable[RBACRole]:
    """
    Collect all children roles of a role, recursively.

    Only has effect if project has RBAC role hierarchy set up.
    """
    yield role
    for child in RBACRole.objects.children_of(role):
        yield from collect_role_children(child)


def get_complete_roles_permissions(roles: Iterable[RBACRole]) -> Mapping[str, str]:
    """
    Return a mapping of permissions to access modes for a given set of roles, recursively following children.
    """

    assert isinstance(roles, Iterable), "get_complete_roles_permissions(): roles must be an iterable"

    return merge_permissions(flatten(collect_role_children(role) for role in roles))


def get_instance_rbac_roles(user: AbstractUser, model: type[models.Model], instance_id: int) -> Iterable[RBACRole]:
    """
    Return all roles directly assigned to a user for a particular instance of a model.
    This function is the root for getting roles, as its implementation may change to include
    caching, other databases, etc.

    Current implementation falls back to the ORM selects, and is very inefficient.

    TODO: introduce caching
    """
    return RBACRole.objects.filter(
        pk__in=InstanceRoleAssignment.objects.filter(
            model=f"{model._meta.app_label}__{model._meta.model_name}",  # noqa: SLF001
            instance_id=instance_id,
            user=user,
        ).values_list("role", flat=True),
    )


def get_complete_instance_rbac_roles(
    user: AbstractUser,
    model: type[models.Model],
    instance_id: int,
) -> Iterable[RBACRole] | Error:
    """
    Return all roles assigned to a user for a particular instance of a model, recursively following children models.
    This function is the root for getting roles, as its implementation may change to include
    caching, other databases, etc.

    Keep in mind that this function also includes non-instance-level roles, so this is to-go function if you want to
    obtain roles for serializer/view permission checking.
    """
    inst = model.objects.filter(pk=instance_id).first()
    if inst is None:
        return Error(
            error_code=codes.does_not_exist,
            eng_description=(
                f"Instance of {model._meta.app_label}.{model._meta.model_name} "  # noqa: SLF001
                "with id={instance_id} does not exist"
            ),
            ui_description=(
                f"Instance of {model._meta.app_label}.{model._meta.model_name} "  # noqa: SLF001
                "with id={instance_id} does not exist"
            ),
        )

    all_models = get_all_rbac_model_parents(inst)
    roles = flatten(
        [get_complete_rbac_roles(user)]
        + [get_instance_rbac_roles(user, instance.__class__, instance.pk) for instance in all_models],
    )

    logging.warning(f"Retrieved roles: {roles}")

    def recurse(role: RBACRole) -> Iterable[RBACRole]:
        yield role
        for child in RBACRole.objects.children_of(role):
            yield from recurse(child)

    return itertools.chain.from_iterable(recurse(role) for role in roles)


def get_access_mode_for_permission(
    permissions: Mapping[str, str],
    permission: str,
) -> str | None:
    """
    Return access mode for a particular permission for a given set of permissions.
    """
    return permissions.get(permission, None)


def has_access_to_entire_model(
    permissions: Mapping[str, str],
    model: type[models.Model],
    mode: str,
) -> bool:
    """
    Check if given dict of permissions provides access to the given model with given access mode.

    Available access mode characters: c (create), r (read), u (update), d (delete).
    """

    model_name: str = f"{model._meta.app_label}__{model._meta.model_name}"  # noqa: SLF001

    # Find the permission for requested model
    return any(
        permission_name == model_name and all(m in access_mode for m in mode)
        for permission_name, access_mode in permissions.items()
    )



def get_allowed_model_fields(permissions: Mapping[str, str], model: str, mode: str) -> list[str]:
    """
    Return a list of fields that user has access to with a given access mode.
    """
    return [
        permission_name.split("__")[-1]
        for permission_name, access_mode in permissions.items()
        # Filter by matching model name and access mode. Permission name split by "__" should have 3 parts in order to
        # be a field permission (not model permission).
        if len(permission_name.split("__")) == 3
        and "__".join(permission_name.split("__")[0:2]) == model
        and all(m in access_mode for m in mode)
    ]


def has_access_to_model_field(
    permissions: Mapping[str, str],
    model: type[models.Model],
    field_name: str,
    mode: str,
) -> bool:
    """
    Check if given dict of permissions provides access to the given field of a given model with given access mode.

    Available access mode characters: r (read), w (write), d (delete).
    """

    full_field_name: str = f"{model._meta.app_label}__{model._meta.model_name}__{field_name}"  # noqa: SLF001
    # Find the permission for requested model
    for permission_name, access_mode in permissions.items():
        # Check if permission name matches and all requested access modes are present
        if permission_name == full_field_name and all(m in access_mode for m in mode):
            return True

    return False


def merge_permissions(roles: Iterable[RBACRole]) -> Mapping[str, str]:
    """
    Merge all given roles' permissions into a single dict, removing duplicate
    keys and merging their access modes.
    """
    all_permissions: dict[str, list[str]] = defaultdict(list)

    for role in roles:
        for permission, access_modes in role.get_permissions().items():
            all_permissions[permission].append(access_modes)

    # Merge duplicate access modes
    cleaned_permissions: dict[str, str] = {}
    for k, v in all_permissions.items():
        cleaned_permissions[k] = "".join(set(flatten(v)))

    return cleaned_permissions


def get_all_rbac_model_parents(model: models.Model) -> Iterable[models.Model]:
    """
    Return all recursive parents of the given RBAC-hierarchy-enabled model instance.
    """
    local_model: models.Model | None = model
    yield model
    while isinstance(local_model, RBACHierarchyModelMixin):
        local_model = local_model.get_rbac_parent()
        if local_model is not None:
            yield local_model
