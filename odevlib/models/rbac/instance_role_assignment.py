from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Manager

from odevlib.fields.rbac_model import RBACModelField
from odevlib.models import OModel, RBACRole


class InstanceRoleAssignmentManager(Manager):
    def roles_for_instance(
        self,
        user: AbstractUser,
        model_name: str,
        instance_id: int,
    ) -> list[RBACRole]:
        return list(
            InstanceRoleAssignment.objects.filter(
                model=model_name,
                instance_id=instance_id,
                user=user,
            ).values_list(
                "role",
                flat=True,
            ),
        )


class InstanceRoleAssignment(OModel):
    """
    Represents assignment of a RBACRole to a user only for a particular instance of a particular model.
    """

    class Meta:
        verbose_name = "Role assignment for instance"
        verbose_name_plural = "Role assignments for instances"

    role = models.ForeignKey(RBACRole, verbose_name="Role", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="User", on_delete=models.CASCADE)
    model = RBACModelField(verbose_name="Full model name")
    instance_id = models.IntegerField(verbose_name="ID of a particular model instance")

    objects: InstanceRoleAssignmentManager = InstanceRoleAssignmentManager()

    def __str__(self) -> str:
        return f"{self.user.username} — {self.model}[{self.instance_id}] — {self.role.name}"
