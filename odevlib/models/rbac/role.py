from collections.abc import Mapping

from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import HStoreField
from django.db import models
from django.db.models.manager import Manager

from odevlib.exceptions.immutable import ImmutableException
from odevlib.models import OModel


class RBACRoleManager(Manager["RBACRole"]):
    def for_user(self, user: AbstractUser) -> models.QuerySet["RBACRole"]:
        return self.filter(rbac_assignments__user=user)

    def children_of(self, role: "RBACRole") -> models.QuerySet["RBACRole"]:
        return self.filter(hierarchy_parents__parent_role=role)


class RBACRole(OModel):
    """
    RBACRole uses OModel as the base to keep track of object changes. This improves auditability.
    """

    class Meta:
        verbose_name = "RBAC Role"
        verbose_name_plural = "RBAC Roles"

    name = models.TextField(verbose_name="Название роли")
    ui_name = models.TextField(verbose_name="Название роли для UI")
    permissions: HStoreField = HStoreField(verbose_name="Permissions assigned to this role")

    objects: RBACRoleManager = RBACRoleManager()

    def get_permissions(self) -> Mapping[str, str]:
        """
        Type-safe retrieval of permissions mapping.
        """
        return self.permissions

    def set_permissions(self, new_perms: Mapping[str, str]) -> None:
        """
        Permissions is only meant to store immutable Mapping[str, str], but HStoreField allows for
        dict[str, str | None]. To stop static analyzers from complaining about incompatible types,
        we need this type-safe method.

        This method does not touch the database, it only updates the in-memory instance.

        More info: https://stackoverflow.com/questions/73603289/why-doesnt-parameter-type-dictstr-unionstr-int-accept-value-of-type-di
        """
        self.permissions = new_perms

    def save(self, *args, **kwargs) -> None:
        if self.pk:
            # Obtain the still unmodified version from database and ensure that name was not changed.
            # Postgres trigger will still prevent alteration of the name, but handling this in Django additionally
            # allows to return a pretty human-readable error.
            current: RBACRole = RBACRole.objects.get(pk=self.pk)
            if 'name' in kwargs and current.name != kwargs['name']:
                raise ImmutableException(
                    message="Can't modify RBACRole name, as it is immutable",
                    ui_message="Can't modify RBACRole name, as it is immutable",
                )
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} — {self.ui_name}"
