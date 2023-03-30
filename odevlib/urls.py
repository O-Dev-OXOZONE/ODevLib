from django.urls import path
from rest_framework.routers import SimpleRouter

from odevlib.views.rbac.permissions import do_i_have_rbac_permission, list_all_rbac_permissions
from odevlib.views.rbac.rbac_role import RBACRoleViewSet

router = SimpleRouter()

router.register('rbacrole', RBACRoleViewSet)

urlpatterns = [
    path('do_i_have_rbac_permission/', do_i_have_rbac_permission),
    path('list_rbac_permissions/', list_all_rbac_permissions),
]

urlpatterns += router.urls  # type: ignore
