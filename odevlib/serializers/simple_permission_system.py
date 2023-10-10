from rest_framework import serializers

from odevlib.models.simple_permission_system import SimplePermissionSystemPermission


class SimplePermissionSystemPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimplePermissionSystemPermission
        fields = (
            "id",
            "subsystem",
            "name",
            "can_create",
            "can_read",
            "can_update",
            "can_delete",
        )


class SimplePermissionSystemPermissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimplePermissionSystemPermission
        fields = (
            "subsystem",
            "name",
            "can_create",
            "can_read",
            "can_update",
            "can_delete",
        )
