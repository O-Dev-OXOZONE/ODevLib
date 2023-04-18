from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from odevlib.models import RBACRole
from odevlib.models.omodel import OModel


class RoleAssignment(OModel):
    """
    Represents an assignment of a RBACRole to user.
    """

    class Meta:
        verbose_name = "Присвоение роли"
        verbose_name_plural = "Присвоения ролей"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователь",
        on_delete=models.CASCADE,
        related_name="rbac_assignments",
    )
    role = models.ForeignKey(
        RBACRole,
        verbose_name="Роль",
        on_delete=models.CASCADE,
        related_name="rbac_assignments",
    )

    def __str__(self):
        return f"{self.user.username} — {self.role}"
