from odevlib.models.simple_permission_system import SimplePermissionSystemPermission
from odevlib.permissions import simple_viewset_permission
from odevlib.serializers.simple_permission_system import (
    SimplePermissionSystemPermissionCreateSerializer,
    SimplePermissionSystemPermissionSerializer,
)
from odevlib.views.oviewset import OModelViewSet


class SimplePermissionSystemPermissionViewSet(OModelViewSet):
    queryset = SimplePermissionSystemPermission.objects.all()
    serializer_class = SimplePermissionSystemPermissionSerializer
    create_serializer_class = SimplePermissionSystemPermissionCreateSerializer
    permission_classes = (simple_viewset_permission("sps"),)
