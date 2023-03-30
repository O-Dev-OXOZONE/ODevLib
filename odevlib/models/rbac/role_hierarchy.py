from django.db.models import CASCADE, ForeignKey

from odevlib.models import OModel, RBACRole


class RoleHierarchyEntry(OModel):
    """
    Represents parent-child relation between two RBACRoles.
    """

    class Meta:
        verbose_name = "Role Hierarchy Entry"
        verbose_name_plural = "Role Hierarchy Entries"

    parent_role = ForeignKey(
        RBACRole,
        verbose_name="Parent role",
        related_name="hierarchy_children",
        on_delete=CASCADE,
    )
    child_role = ForeignKey(
        RBACRole,
        verbose_name="Child role",
        related_name="hierarchy_parents",
        on_delete=CASCADE,
    )

    def __str__(self):
        return f'"{self.child_role}" child of "{self.parent_role}"'
