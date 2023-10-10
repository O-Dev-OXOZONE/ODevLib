from django.contrib import admin

from odevlib.admin.omodel import OModelAdmin
from odevlib.models import RBACRole
from odevlib.models.rbac.instance_role_assignment import InstanceRoleAssignment
from odevlib.models.rbac.role_assignment import RoleAssignment
from odevlib.models.rbac.role_hierarchy import RoleHierarchyEntry

try:
    admin.site.register(RBACRole, OModelAdmin)
    admin.site.register(RoleAssignment, OModelAdmin)
    admin.site.register(RoleHierarchyEntry, OModelAdmin)
    admin.site.register(InstanceRoleAssignment, OModelAdmin)
except admin.sites.AlreadyRegistered:
    pass
