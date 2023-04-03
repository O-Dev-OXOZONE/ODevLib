from typing import Callable

from django.contrib.auth.models import AbstractUser
from rest_framework.exceptions import APIException
from rest_framework.permissions import BasePermission, SingleOperandHolder

from odevlib.models.simple_permission_system import SimplePermissionAssignment, SimplePermissionSystemPermission


class BlockedPermission(BasePermission):
    def has_permission(self, request, view):
        return False


class SimplePermission(BasePermission):
    """
    Checks user's permissions against SimplePermission.
    """

    create_methods = ["POST"]
    read_methods = ["GET", "OPTIONS", "HEAD"]
    update_methods = ["PUT", "PATCH"]
    delete_methods = ["DELETE"]

    permission_name: str

    def __init__(self, permission_name: str) -> None:
        super().__init__()
        self.permission_name = permission_name

    def has_permission(self, request, view) -> bool:
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, "_ignore_model_permissions", False):
            return True

        # Ensure user is available and authenticated
        if not request.user or not request.user.is_authenticated:
            print("NO USER OR NOT AUTHENTICATED")
            return False

        user = request.user
        assert isinstance(user, AbstractUser)

        if user.is_superuser:
            return True

        is_create: bool = request.method in self.create_methods
        is_read: bool = request.method in self.read_methods
        is_update: bool = request.method in self.update_methods
        is_delete: bool = request.method in self.delete_methods

        # TODO: check if this filter works correctly
        qs = SimplePermissionSystemPermission.objects.filter(
            pk__in=(
                SimplePermissionAssignment.objects.filter(
                    permission__subsystem=self.permission_name, user=user
                ).values_list("permission", flat=True)
            )
        )

        # Pick the appropriate access mode
        if is_create:
            qs = qs.filter(can_create=True)
        elif is_read:
            qs = qs.filter(can_read=True)
        elif is_update:
            qs = qs.filter(can_update=True)
        elif is_delete:
            qs = qs.filter(can_delete=True)
        else:
            raise APIException("Unknown method")

        if qs.count() > 0:
            return True
        return False


def simple_viewset_permission(perm: str) -> SingleOperandHolder:
    class SimplePermissionOperandHolder(SingleOperandHolder):
        def __init__(self):
            super().__init__(None, None)  # type: ignore

        def __call__(self, *args, **kwargs):
            return SimplePermission(perm)

    return SimplePermissionOperandHolder()

    # return lambda: SimplePermission(perm)


def simple_permission(perm: str):
    def decorator(func):
        func.permission_classes = [lambda: SimplePermission(perm)]
        return func

    return decorator
