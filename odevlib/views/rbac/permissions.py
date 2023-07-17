from typing import Optional
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

from odevlib.errors import codes
from odevlib.models.errors import Error
from odevlib.business_logic.rbac import permissions
from odevlib.models.rbac.role import RBACRole
from odevlib.serializers.rbac.user_roles import MyRolesAndPermissionsSerializer


@extend_schema(
    summary="Проверить, есть ли у меня запрашиваемое право",
    description='Возвращает "None" если на данное право нет ни одного режима доступа, '
    'либо комбинацию из режимов доступа "c", "r", "u" и "d", если соответствующие '
    "доступы есть (режимы доступа могут идти в произвольном порядке).\n\n"
    "Имеет 3 режима проверки:\n"
    "1. Прямая проверка через роли, присвоенные пользователю.\n"
    "2. Проверка instance-level прав для конкретного инстанса конкретной модели. "
    "Используется, когда переданы поля `model_name` и `instance_id`.\n"
    "3. Проверка instance-level прав, используя родительскую сущность. Полезно в "
    "случаях, когда мы создаем новый инстанс через POST запрос и не можем "
    "напрямую проверить наши права на создание, так как инстанса для проверки "
    "в БД еще не существует. Используется, когда переданы поля `parent_model` и "
    "`parent_id`.",
    request=None,
    parameters=[
        OpenApiParameter(
            "permission",
            description="Обязательный параметр, указывающий на название конкретного права, которое "
            "клиент хочет проверить. Это может быть целая модель или отдельное поле "
            "модели.\n\n"
            "Формат: `appname__modelname[__fieldname]`.",
            location=OpenApiParameter.QUERY,
            type=OpenApiTypes.STR,
            required=True,
        ),
        OpenApiParameter(
            "model_name",
            description="**[Для instance-level RBAC]**\n\n"
            "Название модели, которую клиент просит использовать для проверки "
            "instance-level роли.\n\n"
            "Формат: `appname__modelname`",
            location=OpenApiParameter.QUERY,
            type=OpenApiTypes.STR,
            required=False,
        ),
        OpenApiParameter(
            "instance_id",
            description="**[Для instance-level RBAC]**\n\n"
            "ID инстанса, которую клиент просит использовать для проверки "
            "instance-level роли. Связан с параметром `model_name`, "
            "инстанс с этим ID берется именно для модели `model_name`.",
            location=OpenApiParameter.QUERY,
            type=OpenApiTypes.INT,
            required=False,
        ),
        OpenApiParameter(
            "parent_model",
            description="**[Для создания дочерних instance-level RBAC сущностей]**\n\n"
            "Название модели, которую клиент просит использовать для проверки "
            "instance-level роли при проверке родительской модели.\n\n"
            "Это поле используется при проверке прав при создании нового инстанса, "
            "когда инстанс еще не существует и вызвать проверку для него "
            "еще нельзя, но создаем эту сущность мы внутри другой RBAC-aware "
            "сущности, роль внутри которой может давать права на все дочерние "
            "сущности.\n\n"
            "Формат: `appname_modelname`\n\n"
            "Пример: у нас есть пользователь и мы хотим создать под ним новый заказ. "
            "Доступ к пользователям и заказам управляется RBACом. "
            "Так как заказ еще не создан, мы не может проверить, есть ли у нас право "
            "на доступ к созданию нового заказа. Но зато у нас есть право на доступ ко "
            "всем дочерним сущностям нашего пользователя, и при создании заказа мы "
            "можем определить наш доступ к созданию исходя из инстанса пользователя.",
            location=OpenApiParameter.QUERY,
            type=OpenApiTypes.STR,
            required=False,
        ),
        OpenApiParameter(
            "parent_id",
            description="**[Для создания дочерних instance-level RBAC сущностей]**\n\n"
            "ID инстанса родительской модели, который будет использоваться для "
            "проверки доступа к новосоздаваемому дочернему инстансу.",
            location=OpenApiParameter.QUERY,
            type=OpenApiTypes.INT,
            required=False,
        ),
    ],
    responses={200: serializers.CharField()},
)
@api_view()
@permission_classes([IsAuthenticated])
def do_i_have_rbac_permission(request: Request, *args, **kwargs) -> Response:
    """
    Execution logic:
    - If we only have permission_name, we get all global roles and return access mode for a requested permission.
    - If we also have model_name and instance_id, we get all instance-level roles and return access mode for a requested permission.
    - If we also have parent_model and parent_id, we get all instance-level roles for parent_model and return access mode for a requested permission.
    """
    permission_name: Optional[str] = request.query_params.get("permission", None)
    model_name: Optional[str] = request.query_params.get("model_name", None)
    instance_id: Optional[str] = request.query_params.get("instance_id", None)
    parent_model: Optional[str] = request.query_params.get("parent_model", None)
    parent_id: Optional[str] = request.query_params.get("parent_id", None)

    user = request.user
    assert isinstance(user, AbstractUser)

    ### Checks start ###
    if permission_name is None:
        return Error(
            error_code=codes.invalid_request_data,
            eng_description=f'"permission" param was not passed',
            ui_description=f'Параметр "permission" не был передан',
        ).serialize_response()

    if model_name is not None:
        if len(model_name.split("__")) != 2:
            return Error(
                error_code=codes.invalid_request_data,
                eng_description=f"Expected model_name to contain two parts separated by __",
                ui_description=f"model_name должен содержать две части, разделенные __",
            ).serialize_response()
        try:
            model_type = apps.get_model(model_name.replace("__", "."))
        except LookupError:
            return Error(
                error_code=codes.invalid_request_data,
                eng_description=f'Could not find model "{model_name}"',
                ui_description=f'Не найдена модель "{model_name}"',
            ).serialize_response()

    if instance_id is not None:
        try:
            instance_id_int = int(instance_id)
        except ValueError:
            return Error(
                error_code=codes.invalid_request_data,
                eng_description=f'Expected int in instance_id, but got "{instance_id}"',
                ui_description=f'В instance_id ожидался int, был получен "{instance_id}"',
            ).serialize_response()

    if parent_model is not None:
        if len(parent_model.split("__")) != 2:
            return Error(
                error_code=codes.invalid_request_data,
                eng_description=f"Expected parent_model to contain two underscores, got {len(parent_model.split('__'))}",
                ui_description=f"parent_model должен содержать два подчеркивания, получено {len(parent_model.split('__'))}",
            ).serialize_response()
        try:
            parent_model_type = apps.get_model(parent_model.replace("__", "."))
        except LookupError:
            return Error(
                error_code=codes.invalid_request_data,
                eng_description=f'Could not find model "{parent_model}"',
                ui_description=f'Не найдена модель "{parent_model}"',
            ).serialize_response()

    if parent_id is not None:
        try:
            parent_id_int = int(parent_id)
        except ValueError:
            return Error(
                error_code=codes.invalid_request_data,
                eng_description=f'Expected int in parent_id, but got "{instance_id}"',
                ui_description=f'В parent_id ожидался int, был получен "{instance_id}"',
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
        value = "".join(set(*value, *model_value))

    return Response(str(value))


@extend_schema(
    summary="Получить список всех RBAC ролей и прав текущего пользователя",
    request=None,
    description="Возвращает список всех ролей и прав текущего пользователя. "
    'Если переданы параметры "model_name" и "instance_id", проверяет еще '
    "и instance-level роли для заданной сущности.",
    parameters=[
        OpenApiParameter(
            "model_name",
            description="**[Для instance-level RBAC]**\n\n"
            "Название модели, которую клиент просит использовать для проверки "
            "instance-level роли.\n\n"
            "Формат: `appname_modelname`",
            location=OpenApiParameter.QUERY,
            type=OpenApiTypes.STR,
            required=False,
        ),
        OpenApiParameter(
            "instance_id",
            description="**[Для instance-level RBAC]**\n\n"
            "ID инстанса, которую клиент просит использовать для проверки "
            "instance-level роли. Связан с параметром `model_name`, "
            "инстанс с этим ID берется именно для модели `model_name`.",
            location=OpenApiParameter.QUERY,
            type=OpenApiTypes.INT,
            required=False,
        ),
    ],
    responses={200: MyRolesAndPermissionsSerializer()},
)
@api_view()
def get_my_roles_and_permissions(request: Request, *args, **kwargs) -> Response:
    model_name: Optional[str] = request.query_params.get("model_name", None)
    instance_id: Optional[str] = request.query_params.get("instance_id", None)

    user = request.user
    assert isinstance(user, AbstractUser)

    if model_name is not None:
        # Handle instance-level case
        if len(model_name.split("__")) != 2:
            return Error(
                error_code=codes.invalid_request_data,
                eng_description=f"Expected model_name to contain two parts separated by __",
                ui_description=f"model_name должен содержать две части, разделенные __",
            ).serialize_response()
        try:
            model_type = apps.get_model(model_name.replace("__", "."))
        except LookupError:
            return Error(
                error_code=codes.invalid_request_data,
                eng_description=f'Could not find model "{model_name}"',
                ui_description=f'Не найдена модель "{model_name}"',
            ).serialize_response()

    if instance_id is not None:
        try:
            instance_id_int = int(instance_id)
        except ValueError:
            return Error(
                error_code=codes.invalid_request_data,
                eng_description=f'Expected int in instance_id, but got "{instance_id}"',
                ui_description=f'В instance_id ожидался int, был получен "{instance_id}"',
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
                    "roles": map(lambda role: role.name, roles),
                    "permissions": perms,
                }
            ).data
        )
    else:
        # Return global roles and permissions
        roles = list(permissions.get_direct_rbac_roles(user))
        perms = permissions.merge_permissions(roles)
        return Response(
            MyRolesAndPermissionsSerializer(
                {
                    "roles": map(lambda role: role.name, roles),
                    "permissions": perms,
                }
            ).data
        )


@extend_schema(
    summary="Получить список всех RBAC прав",
    request=None,
    responses={200: serializers.ListSerializer(child=serializers.CharField())},
)
@api_view()
@permission_classes([IsAuthenticated])
def list_all_rbac_permissions(request: Request, *args, **kwargs) -> Response:
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
            app_name = model._meta.app_label
            # noinspection PyProtectedMember
            model_name = model._meta.model_name
            fields = [field for field in serializer_class.Meta.fields] + [
                field for field in create_serializer_class.Meta.fields
            ]

            results.append(f"{app_name}__{model_name}")
            results.extend([f"{app_name}__{model_name}__{field_name}" for field_name in fields])

    results = sorted(list(set(results)))

    return Response(results)
