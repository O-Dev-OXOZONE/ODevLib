from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from odevlib.models import OModel


class SimplePermissionSystemPermission(OModel):
    """
    Simple permission system allows to create permissions that control entire subsystems. They can be assigned to view/viewsets.

    It is expected that project that uses ODevLib will have its own enum with short_names that will match this model,
    so the code doesn't contain magic strings.

    ODevLib adds only one entry to this table --- ("rbac", "RBAC") --- which controls access to RBAC configuration
    views.

    Example of such class:
    ```
    class Permissions:
        CORE = "core"
        USERS = "users"
        ORDERS = "orders"
        ...
    ```
    """

    subsystem = models.CharField(
        verbose_name="Subsystem",
        max_length=255,
        help_text="Subsystem that this permission is responsible for. Permission checker only looks for this field.",
    )
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Name",
        help_text="Name of the permission. Used in UI. Must be unique.",
    )

    # CRUD permissions of the role
    can_create = models.BooleanField()
    can_read = models.BooleanField()
    can_update = models.BooleanField()
    can_delete = models.BooleanField()

    class Meta:
        verbose_name = "Simple permission"
        verbose_name_plural = "Simple permissions"


class SimplePermissionAssignment(OModel):
    """
    Represents assignment of a simple permission system permission to a user.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="User",
        on_delete=models.CASCADE,
    )
    permission = models.ForeignKey(
        SimplePermissionSystemPermission,
        verbose_name="Permission",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Simple permission assignment"
        verbose_name_plural = "Simple permission assignments"
        unique_together = (("user", "permission"),)
