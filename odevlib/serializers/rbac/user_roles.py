

from rest_framework import serializers


class MyRolesAndPermissionsSerializer(serializers.Serializer):
    """Serializer for get_my_roles_and_permissions view."""
    roles = serializers.ListField(
        child=serializers.CharField(),
        help_text='List of RBAC roles the user has in the given context.'
    )
    permissions = serializers.DictField(
        # Key is always a string, because of JSON specification.
        # Value has child serializer.
        child=serializers.CharField(),
        help_text='List of permissions the user has in the given context.'
    )
