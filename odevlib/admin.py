from django.contrib import admin
from django.contrib.auth.models import User, AbstractUser

from odevlib.models import RBACRole
from odevlib.models.rbac.instance_role_assignment import InstanceRoleAssignment
from odevlib.models.rbac.role_assignment import RoleAssignment
from odevlib.models.rbac.role_hierarchy import RoleHierarchyEntry


class OModelAdmin(admin.ModelAdmin):
    readonly_fields = ["created_by", "updated_by"]

    def save_model(self, request, obj: InstanceRoleAssignment, form, change) -> None:
        user: User = request.user
        assert isinstance(user, AbstractUser)
        obj.save(user=user)


admin.site.register(RBACRole, OModelAdmin)
admin.site.register(RoleAssignment, admin.ModelAdmin)
admin.site.register(RoleHierarchyEntry, OModelAdmin)
admin.site.register(InstanceRoleAssignment, OModelAdmin)
