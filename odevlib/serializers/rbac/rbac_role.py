from odevlib.models import RBACRole
from odevlib.serializers import OModelCreateSerializer, OModelSerializer
from odevlib.serializers.rbac_serializer import RBACCreateSerializer, RBACSerializer


class RBACRoleSerializer(RBACSerializer):
    class Meta(OModelSerializer.Meta):
        model = RBACRole
        fields = OModelSerializer.Meta.fields + (
            "id",
            "name",
            "ui_name",
            "permissions",
        )


class RBACRoleCreateSerializer(RBACCreateSerializer):
    class Meta(OModelCreateSerializer.Meta):
        model = RBACRole
        fields = (
            "id",
            "name",
            "ui_name",
            "permissions",
        )
