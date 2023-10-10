from typing import TYPE_CHECKING

from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from odevlib.business_logic.rbac.permissions import get_complete_roles_permissions
from odevlib.errors import codes
from odevlib.models import RBACRole
from odevlib.models.errors import Error
from odevlib.permissions import simple_viewset_permission
from odevlib.serializers.rbac.rbac_role import RBACRoleCreateSerializer, RBACRoleSerializer
from odevlib.views import OModelViewSet

if TYPE_CHECKING:
    from collections.abc import Mapping


class RBACRoleViewSet(OModelViewSet[RBACRole]):
    queryset = RBACRole.objects.all()
    serializer_class = RBACRoleSerializer
    create_serializer_class = RBACRoleCreateSerializer
    permission_classes = (simple_viewset_permission("rbac"),)
    use_rbac = True

    @action(methods=["GET"], detail=True)
    def complete_permissions(self, request: Request, pk: int) -> Response:  # noqa: ARG002
        role: RBACRole | Error = self.get_object()
        if isinstance(role, Error):
            return Error(
                error_code=codes.does_not_exist,
                eng_description="Role with given ID does not exist",
                ui_description="Role with given ID does not exist",
            ).serialize_response()

        complete_permissions: Mapping[str, str] = get_complete_roles_permissions([role])
        role.permissions = complete_permissions

        serializer = RBACRoleSerializer(role, context={"action": "retrieve"})
        return Response(serializer.data)
