from typing import TYPE_CHECKING, TypeAlias, TypeVar, Union
import typing

from django.db import models
from django.db.models import ProtectedError
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from odevlib.business_logic.rbac.permissions import (
    get_complete_instance_rbac_roles,
    has_access_to_entire_model,
    merge_permissions,
)
from odevlib.business_logic.relations import get_relations
from odevlib.errors import codes
from odevlib.models.errors import Error
from odevlib.prefetching import prefetch
from odevlib.serializers.related import RelationSerializer
from django.db.models import QuerySet
from typing import Generic

if TYPE_CHECKING:
    from odevlib.views.oviewset import OViewSetProtocol


M = TypeVar("M", bound=models.Model)


class OCreateMixin(Generic[M]):
    """
    Provides create method for OViewSet.
    """

    def create(self: "OViewSetProtocol[M]", request, *args, **kwargs) -> Response:
        # Prepare additional kwargs, which contain non-pk URL lookup fields and profile of requester.
        additional_kwargs = kwargs.copy()
        additional_kwargs.pop(self.lookup_url_kwarg, None)
        context = {
            "additional_kwargs": additional_kwargs,
            "user": request.user,
            "request": request,
            "action": "create",
        }

        if self.create_serializer_class is None:
            return Error(
                error_code=codes.internal_server_error,
                eng_description="Create serializer class is not specified",
                ui_description="Create serializer class is not specified",
            ).serialize_response()
        if self.serializer_class is None:
            return Error(
                error_code=codes.internal_server_error,
                eng_description="Serializer class is not specified",
                ui_description="Serializer class is not specified",
            ).serialize_response()

        serializer = self.create_serializer_class(data=request.data, context=context)

        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_serializer = self.serializer_class(instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class OListMixin(Generic[M]):
    """
    Provides list method for OViewSet.
    """

    def list(self: "OViewSetProtocol[M]", request, *args, **kwargs) -> Response:
        # Prepare additional kwargs, which contain non-pk URL lookup fields and profile of requester.
        additional_kwargs = kwargs.copy()
        additional_kwargs.pop(self.lookup_url_kwarg, None)
        context = {
            "additional_kwargs": additional_kwargs,
            "user": request.user,
            "request": request,
            "action": "list",
        }

        if self.serializer_class is None:
            return Error(
                error_code=codes.internal_server_error,
                eng_description="Serializer class is not specified",
                ui_description="Serializer class is not specified",
            ).serialize_response()
        queryset: QuerySet = prefetch(
            self.get_queryset(), self.serializer_class, context=context
        )
        if hasattr(self, "filter_backends"):
            for backend in list(self.filter_backends):
                queryset = backend().filter_queryset(request, queryset, self)

        serializer = self.serializer_class(queryset, many=True, context=context)
        return Response(serializer.data)


class OCursorPaginatedListMixin(Generic[M]):
    """
    Provides list method with support for cursor pagination for OViewSet:
    user should pass the starting point, direction and count of items to retrieve.

    You can only get primary-key-ordered results when using this type of pagination.

    If no query parameters are passed, than all results are returned without any pagination.
    """

    def list(self: "OViewSetProtocol[M]", request, *args, **kwargs) -> Response:
        # Prepare additional kwargs, which contain non-pk URL lookup fields and profile of requester.
        additional_kwargs = kwargs.copy()
        additional_kwargs.pop(self.lookup_url_kwarg, None)
        context = {
            "additional_kwargs": additional_kwargs,
            "user": request.user,
            "request": request,
            "action": "list",
        }

        # Used when navigating backward
        first_id: str | None = request.query_params.get("start_id", None)
        # Used when navigating forward
        last_id: str | None = request.query_params.get("last_id", None)

        count_str: str = request.query_params.get("count", "50")
        try:
            count = int(count_str)
        except ValueError:
            return Error(
                error_code=codes.invalid_request_data,
                eng_description="Count parameter must be int",
                ui_description="Count parameter must be int",
            ).serialize_response()

        if first_id is not None and last_id is not None:
            return Error(
                error_code=codes.invalid_request_data,
                eng_description="Can't use both first_id and last_id. Please specify only one argument.",
                ui_description="Can't use both first_id and last_id. Please specify only one argument.",
            ).serialize_response()

        if self.serializer_class is None:
            return Error(
                error_code=codes.internal_server_error,
                eng_description="Serializer class is not specified",
                ui_description="Serializer class is not specified",
            ).serialize_response()

        queryset: QuerySet[M] = self.get_queryset()

        if first_id is not None:
            queryset = queryset.filter(pk__lt=first_id).order_by("pk")
            queryset = queryset[:count]
        elif last_id is not None:
            queryset = queryset.filter(pk__gt=last_id).order_by("pk")
            queryset = queryset[:count]

        queryset = prefetch(queryset, self.serializer_class, context=context)
        if hasattr(self, "filter_backends"):
            for backend in list(self.filter_backends):
                queryset = backend().filter_queryset(request, queryset, self)

        serializer = self.serializer_class(queryset, many=True, context=context)
        return Response(serializer.data)


class ORetrieveMixin(Generic[M]):
    """
    Provides retrieve method for OViewSet.
    """

    def retrieve(self: "OViewSetProtocol[M]", request, *args, **kwargs) -> Response:
        instance = self.get_object()
        if isinstance(instance, Error):
            return instance.serialize_response()

        # Prepare additional kwargs, which contain non-pk URL lookup fields and profile of requester.
        additional_kwargs = kwargs.copy()
        additional_kwargs.pop(self.lookup_url_kwarg, None)
        context = {
            "additional_kwargs": additional_kwargs,
            "user": request.user,
            "request": request,
            "action": "retrieve",
        }

        if self.serializer_class is None:
            return Error(
                error_code=codes.internal_server_error,
                eng_description="Serializer class is not specified",
                ui_description="Serializer class is not specified",
            ).serialize_response()
        serializer = self.serializer_class(instance, context=context)

        return Response(serializer.data)


class OUpdateMixin(Generic[M]):
    """
    Provides put/patch methods for OViewSet.
    """

    def update(self: "OViewSetProtocol[M]", request, *args, **kwargs) -> Response:
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        if isinstance(instance, Error):
            return instance.serialize_response()

        # Prepare additional kwargs, which contain non-pk URL lookup fields and profile of requester.
        additional_kwargs = kwargs.copy()
        additional_kwargs.pop(self.lookup_url_kwarg, None)
        context = {
            "additional_kwargs": additional_kwargs,
            "user": request.user,
            "request": request,
            "action": "update",
        }

        if self.serializer_class is None:
            return Error(
                error_code=codes.internal_server_error,
                eng_description="Serializer class is not specified",
                ui_description="Serializer class is not specified",
            ).serialize_response()

        # Decide if dedicated update serializer should be used based on its presence in the viewset class
        if self.update_serializer_class is not None:
            serializer = self.update_serializer_class(
                instance, data=request.data, partial=partial, context=context
            )
        else:
            if self.create_serializer_class is None:
                return Error(
                    error_code=codes.internal_server_error,
                    eng_description="Create serializer class is not specified",
                    ui_description="Create serializer class is not specified",
                ).serialize_response()
            serializer = self.create_serializer_class(
                instance, data=request.data, partial=partial, context=context
            )

        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to forcibly invalidate the prefetch cache on
            # the instance to re-fetch updated data from the database.
            instance._prefetched_objects_cache = {}  # type: ignore

        response_context = {
            "additional_kwargs": additional_kwargs,
            "user": request.user,
            "request": request,
            "action": "retrieve",
        }

        response_serializer = self.serializer_class(instance, context=response_context)
        return Response(response_serializer.data)

    def partial_update(
        self: "OViewSetProtocol[M]", request: Request, *args, **kwargs
    ) -> Response:
        kwargs["partial"] = True
        # TODO: fix this type ignore. Self should be annotated with both OViewSetProtocol and OUpdateMixin.
        # But with Python type system it's impossible to express that.
        return self.update(request, *args, **kwargs)  # type: ignore


class ODestroyMixin(Generic[M]):
    """
    Provides delete method for OViewSet.
    """

    def destroy(self: "OViewSetProtocol[M]", request, *args, **kwargs) -> Response:
        instance = self.get_object()
        if isinstance(instance, Error):
            return instance.serialize_response()

        # Check RBAC permissions
        if self.use_rbac:
            permissions = get_complete_instance_rbac_roles(
                request.user,
                instance._meta.model,
                instance.pk,
            )
            if isinstance(permissions, Error):
                return permissions.serialize_response()

            all_permissions = merge_permissions(permissions)
            has_permission = (
                has_access_to_entire_model(all_permissions, instance._meta.model, "d")
                or request.user.is_superuser
            )
            if not has_permission:
                return Error(
                    error_code=codes.permission_denied,
                    eng_description=f"You do not have access to delete this object",
                    ui_description=f"У вас нет прав на удаление этого объекта",
                ).serialize_response()

        try:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            return Error(
                error_code=codes.protected_instance,
                eng_description="This instance has protected relations with other instances. Delete related first",
                ui_description="Эта сущность имеет защищенные связи с другими сущностями. "
                "Удалите их перед тем, как удалять эту сущность",
            ).serialize_response()


class ORelationsMixin(Generic[M]):
    # noinspection PyProtectedMember
    @extend_schema(
        summary="Получить список всех связей с другими объектами",
        request=None,
        responses={200: RelationSerializer(many=True)},
    )
    @action(["GET"], detail=True)
    def relations(self: "OViewSetProtocol[M]", request, *args, **kwargs) -> Response:
        # noinspection PyUnresolvedReferences
        instance = self.get_object()
        if isinstance(instance, Error):
            return instance.serialize_response()

        # Check RBAC permissions
        if self.use_rbac:
            permissions = get_complete_instance_rbac_roles(
                request.user, instance.__class__, instance.pk
            )
            if isinstance(permissions, Error):
                return permissions.serialize_response()

            all_permissions = merge_permissions(permissions)
            has_permission = (
                has_access_to_entire_model(all_permissions, instance.__class__, "r")
                or request.user.is_superuser
            )
            if not has_permission:
                return Error(
                    error_code=codes.permission_denied,
                    eng_description=f"You do not have access to get this model relations",
                    ui_description=f"У вас нет прав на получение связей этого объекта",
                ).serialize_response()

        result = get_relations(instance)
        response_serializer = RelationSerializer(data=result, many=True)
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data)


class OModelMixins(
    OCreateMixin[M], OUpdateMixin[M], OListMixin[M], ORetrieveMixin[M], ODestroyMixin[M]
):
    """
    Contains all model methods in a single mixin for easy import.
    """
