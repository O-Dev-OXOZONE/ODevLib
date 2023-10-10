from django.apps import apps
from django.contrib.auth.models import AbstractUser
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.schemas.generators import EndpointEnumerator

from odevlib.business_logic.rbac import permissions
from odevlib.errors import codes
from odevlib.models.errors import Error
from odevlib.serializers.rbac.user_roles import MyRolesAndPermissionsSerializer


@extend_schema(
    summary="Check if I have the requested permission",
    description='Returns "None" if there are no access modes for this permission, '
    'or a combination of access modes "c", "r", "u", and "d" if the corresponding '
    "accesses exist (access modes can be in any order).\n\n"
    "Has 3 check modes:\n"
    "1. Direct check through roles assigned to the user.\n"
    "2. Check instance-level permissions for a specific instance of a specific model. "
    "Used when the fields `model_name` and `instance_id` are passed.\n"
    "3. Check instance-level permissions using the parent entity. Useful in "
    "cases when we create a new instance through a POST request and cannot "
    "directly check our permissions for creation, as the instance to check "
    "does not yet exist in the database. Used when the fields `parent_model` and "
    "`parent_id` are passed.",
    request=None,
    parameters=[
        OpenApiParameter(
            "permission",
            description="Required parameter indicating the name of the specific permission that "
            "the client wants to check. It can be a whole model or a specific field "
            "of the model.\n\n"
            "Format: `appname__modelname[__fieldname]`.",
            location=OpenApiParameter.QUERY,
            type=OpenApiTypes.STR,
            required=True,
        ),
        OpenApiParameter(
            "model_name",
            description="**[For instance-level RBAC]**\n\n"
            "The name of the model that the client requests to use for checking "
            "instance-level role.\n\n"
            "Format: `appname__modelname`",
            location=OpenApiParameter.QUERY,
            type=OpenApiTypes.STR,
            required=False,
        ),
        OpenApiParameter(
            "instance_id",
            description="**[For instance-level RBAC]**\n\n"
            "The ID of the instance that the client requests to use for checking "
            "instance-level role. Associated with the `model_name` parameter, "
            "the instance with this ID is taken specifically for the `model_name` model.",
            location=OpenApiParameter.QUERY,
            type=OpenApiTypes.INT,
            required=False,
        ),
        OpenApiParameter(
            "parent_model",
            description="**[For creating child instance-level RBAC entities]**\n\n"
            "The name of the model that the client requests to use for checking "
            "instance-level role when checking the parent model.\n\n"
            "This field is used when checking permissions when creating a new instance, "
            "when the instance does not yet exist and it is not possible to call the check "
            "for it, but we create this entity inside another RBAC-aware "
            "entity, the role inside which can grant permissions to all child "
            "entities.\n\n"
            "Format: `appname_modelname`\n\n"
            "Example: we have a user and we want to create a new order under them. "
            "Access to users and orders is controlled by RBAC. "
            "Since the order has not yet been created, we cannot check if we have the right "
            "to access creating a new order. But we have the right to access all child "
            "entities of our user, and when creating an order, we "
            "can determine our access to creation based on the user instance.",
            location=OpenApiParameter.QUERY,
            type=OpenApiTypes.STR,
            required=False,
        ),
        OpenApiParameter(
            "parent_id",
            description="**[For creating child instance-level RBAC entities]**\n\n"
            "The ID of the parent model instance that will be used for "
            "checking access to the newly created child instance.",
            location=OpenApiParameter.QUERY,
            type=OpenApiTypes.INT,
            required=False,
        ),
    ],
    responses={200: serializers.CharField()},
)
@api_view()
@permission_classes([IsAuthenticated])
def do_i_have_rbac_permission(request: Request) -> Response:
    """
    Return if the current user has a requested RBAC permission.

    Execution logic:
    - If we only have permission_name, we get all global roles and return access mode for a requested permission.
    - If we also have model_name and instance_id, we get all instance-level roles and return access mode for a requested permission.
    - If we also have parent_model and parent_id, we get all instance-level roles for parent_model and return access mode for a requested permission.
    """
    permission_name: str | None = request.query_params.get("permission", None)
    model_name: str | None = request.query_params.get("model_name", None)
    instance_id: str | None = request.query_params.get("instance_id", None)
    parent_model: str | None = request.query_params.get("parent_model", None)
    parent_id: str | None = request.query_params.get("parent_id", None)

    user = request.user
    assert isinstance(user, AbstractUser)

    ### Checks start ###
    if permission_name is None:
        return Error(
            error_code=codes.invalid_request_data,
            eng_description='"permission" param was not passed',
            ui_description='Параметр "permission" не был передан',
        ).serialize_response()

    if model_name is not None:
        if len(model_name.split("__")) != 2:
            return Error(
                error_code=codes.invalid_request_data,
                eng_description="Expected model_name to contain two parts separated by __",
                ui_description="Expected model_name to contain two parts separated by __",
            ).serialize_response()
        try:
            model_type = apps.get_model(model_name.replace("__", "."))
        except LookupError:
            return Error(
                error_code=codes.invalid_request_data,
                eng_description=f'Could not find model "{model_name}"',
                ui_description=f'Could not find model "{model_name}"',
            ).serialize_response()

    if instance_id is not None:
        try:
            instance_id_int = int(instance_id)
        except ValueError:
            return Error(
                error_code=codes.invalid_request_data,
                eng_description=f'Expected int in instance_id, but got "{instance_id}"',
                ui_description=f'Expected int in instance_id, but got "{instance_id}"',
            ).serialize_response()

    if parent_model is not None:
        if len(parent_model.split("__")) != 2:
            return Error(
                error_code=codes.invalid_request_data,
                eng_description=(
                    f"Expected parent_model to contain two underscores, got {len(parent_model.split('__'))}"
                ),
                ui_description=(
                    f"Expected parent_model to contain two underscores, got {len(parent_model.split('__'))}"
                ),
            ).serialize_response()
        try:
            parent_model_type = apps.get_model(parent_model.replace("__", "."))
        except LookupError:
            return Error(
                error_code=codes.invalid_request_data,
                eng_description=f'Could not find model "{parent_model}"',
                ui_description=f'Could not find model "{parent_model}"',
            ).serialize_response()

    if parent_id is not None:
        try:
            parent_id_int = int(parent_id)
        except ValueError:
            return Error(
                error_code=codes.invalid_request_data,
                eng_description=f'Expected int in parent_id, but got "{instance_id}"',
                ui_description=f'Expected int in parent_id, but got "{instance_id}"',
            ).serialize_response()
    ### Checks end ###

    if model_name is not None and instance_id is not None:
        if parent_model is not None and parent_id is not None:
            # Get instance-level permissions using parent model
            _permissions = permissions.get_complete_instance_rbac_roles(
                user,
                parent_model_type,
                parent_id_int,
            )
            if isinstance(_permissions, Error):
                return _permissions.serialize_response()

            perms = permissions.merge_permissions(_permissions)
        else:
            _permissions = permissions.get_complete_instance_rbac_roles(
                user,
                model_type,
                instance_id_int,
            )
            if isinstance(_permissions, Error):
                return _permissions.serialize_response()

            # Get instance-level permissions using model
            perms = permissions.merge_permissions(_permissions)
    else:
        # Get global permissions
        perms = permissions.merge_permissions(permissions.get_complete_rbac_roles(user))

    value = permissions.get_access_mode_for_permission(
        perms,
        permission_name,
    )

    # Since we may have a permission for an entire model, but don't have a permission for a specific field,
    # we also try to get entire morel permissions
    if len(permission_name.split("__")) == 3:
        model_value = permissions.get_access_mode_for_permission(
            perms,
            permission_name.split("__")[0] + "__" + permission_name.split("__")[1],
        )
        if model_value is not None:
            value = model_value if value is None else "".join({*value, *model_value})

    return Response(str(value))


@extend_schema(
    summary="Get a list of all RBAC roles and permissions for the current user",
    request=None,
    description="Returns a list of all roles and permissions for the current user. "
    'If "model_name" and "instance_id" parameters are provided, it also checks '
    "for instance-level roles for the specified entity.",
    parameters=[
        OpenApiParameter(
            "model_name",
            description="**[For instance-level RBAC]**\n\n"
            "The name of the model that the client requests to use for checking "
            "instance-level role.\n\n"
            "Format: `appname__modelname`",
            location=OpenApiParameter.QUERY,
            type=OpenApiTypes.STR,
            required=False,
        ),
        OpenApiParameter(
            "instance_id",
            description="**[For instance-level RBAC]**\n\n"
            "The ID of the instance that the client requests to use for checking "
            "instance-level role. Associated with the `model_name` parameter, "
            "the instance with this ID is specifically taken for the `model_name` model.",
            location=OpenApiParameter.QUERY,
            type=OpenApiTypes.INT,
            required=False,
        ),
    ],
    responses={200: MyRolesAndPermissionsSerializer()},
)
@api_view()
def get_my_roles_and_permissions(request: Request) -> Response:
    model_name: str | None = request.query_params.get("model_name", None)
    instance_id: str | None = request.query_params.get("instance_id", None)

    user = request.user
    assert isinstance(user, AbstractUser)

    if model_name is not None:
        # Handle instance-level case
        if len(model_name.split("__")) != 2:
            return Error(
                error_code=codes.invalid_request_data,
                eng_description="Expected model_name to contain two parts separated by __",
                ui_description="Expected model_name to contain two parts separated by __",
            ).serialize_response()
        try:
            model_type = apps.get_model(model_name.replace("__", "."))
        except LookupError:
            return Error(
                error_code=codes.invalid_request_data,
                eng_description=f'Could not find model "{model_name}"',
                ui_description=f'Could not find model "{model_name}"',
            ).serialize_response()

    if instance_id is not None:
        try:
            instance_id_int = int(instance_id)
        except ValueError:
            return Error(
                error_code=codes.invalid_request_data,
                eng_description=f'Expected int in instance_id, but got "{instance_id}"',
                ui_description=f'Expected int in instance_id, but got "{instance_id}"',
            ).serialize_response()

    if model_name is not None and instance_id is not None:
        # Return instance-level roles and permissions
        _permissions = permissions.get_complete_instance_rbac_roles(user, model_type, instance_id_int)
        if isinstance(_permissions, Error):
            return _permissions.serialize_response()

        roles = list(_permissions)
        perms = permissions.merge_permissions(roles)
        return Response(
            MyRolesAndPermissionsSerializer(
                {
                    "roles": (role.name for role in roles),
                    "permissions": perms,
                },
            ).data,
        )
    else:
        # Return global roles and permissions
        roles = list(permissions.get_direct_rbac_roles(user))
        perms = permissions.merge_permissions(roles)
        return Response(
            MyRolesAndPermissionsSerializer(
                {
                    "roles": (role.name for role in roles),
                    "permissions": perms,
                },
            ).data,
        )


@extend_schema(
    summary="Получить список всех RBAC прав",
    request=None,
    responses={200: serializers.ListSerializer(child=serializers.CharField())},
)
@api_view()
@permission_classes([IsAuthenticated])
def list_all_rbac_permissions(request: Request, *args, **kwargs) -> Response:  # noqa: ARG001
    endpoint_enumerator = EndpointEnumerator()
    endpoints = endpoint_enumerator.get_api_endpoints()

    results = []

    for endpoint in endpoints:
        cls = getattr(endpoint[2], "cls", None)
        if cls is not None and getattr(cls, "use_rbac", False) is True:
            serializer_class = cls.serializer_class
            create_serializer_class = cls.create_serializer_class

            model = serializer_class.Meta.model
            # noinspection PyProtectedMember
            app_name = model._meta.app_label  # noqa: SLF001
            # noinspection PyProtectedMember
            model_name = model._meta.model_name  # noqa: SLF001
            fields = list(serializer_class.Meta.fields) + list(create_serializer_class.Meta.fields)

            results.append(f"{app_name}__{model_name}")
            results.extend([f"{app_name}__{model_name}__{field_name}" for field_name in fields])

    results = sorted(set(results))

    return Response(results)
