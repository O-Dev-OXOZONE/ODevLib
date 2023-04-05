from django.urls import path
from rest_framework.routers import SimpleRouter

from odevlib.views.rbac.permissions import do_i_have_rbac_permission, get_my_roles_and_permissions, list_all_rbac_permissions
from odevlib.views.rbac.rbac_role import RBACRoleViewSet
from odevlib.views.sps import SimplePermissionSystemPermissionViewSet

router = SimpleRouter()

router.register('rbacrole', RBACRoleViewSet)
router.register('sps_permission', SimplePermissionSystemPermissionViewSet)

urlpatterns = [
    path('do_i_have_rbac_permission/', do_i_have_rbac_permission),
    path('list_rbac_permissions/', list_all_rbac_permissions),
    path('get_my_roles_and_permissions/', get_my_roles_and_permissions),
]

urlpatterns += router.urls  # type: ignore
