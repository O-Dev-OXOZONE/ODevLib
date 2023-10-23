import textwrap
from typing import TYPE_CHECKING, Generic, TypeVar, Union

from django.db import models
from django.db.models import ProtectedError, QuerySet
from django_stubs_ext import QuerySetAny
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from odevlib.business_logic.pagination import paginate_queryset
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
        instance = self.perform_create(serializer)
        if isinstance(instance, Error):
            return instance.serialize_response()
        response_serializer = self.serializer_class(instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer) -> M | Error:
        """
        Hook for custom create logic.
        """
        try:
            return serializer.save()
        except Exception as e:
            return Error(
                error_code=codes.internal_server_error,
                eng_description=f"Error while creating object: {e}",
                ui_description="Error while creating object",
            )


class OListMixin(Generic[M]):
    """
    Provides list method for OViewSet.
    """

    def list(self: "OViewSetProtocol[M]", request: Request, *args, **kwargs) -> Response:  # noqa: A003, ARG002
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

        queryset: QuerySet[M] | Error = self.get_queryset()
        if isinstance(queryset, Error):
            return queryset.serialize_response()

        queryset = prefetch(queryset, self.serializer_class, context=context)
        if hasattr(self, "filter_backends"):
            for backend in list(self.filter_backends):
                queryset = backend().filter_queryset(request, queryset, self)

        if isinstance(queryset, Error):
            return queryset.serialize_response()

        serializer = self.serializer_class(queryset, many=True, context=context)
        return Response(serializer.data)


class OCursorPaginatedListMixin(Generic[M]):
    """
    Provides list method with support for cursor pagination for OViewSet:
    user should pass the starting point, direction and count of items to retrieve.

    You can only get primary-key-ordered results when using this type of pagination.

    If no query parameters are passed, than all results are returned without any pagination.
    """

    @extend_schema(
        summary="Get paginated list of objects",
        description=textwrap.dedent(
            """
            Allows to reliably retrieve data by chunks using cursor pagination.

            If no query parameters are passed, than latest `count` rows are returned.
            The first data retrieval is expected to be done without query parameters to get
            the first chunk.

            After you obtain the chunk, it is possible to use `first_id` and `last_id` query parameters
            to retrieve neighboring chunks.
            """,
        ),
        request=None,
        responses={200: list},
        parameters=[
            OpenApiParameter(
                name="first_id",
                description="ID of the first available object. New objects will go backwards with respect to this ID",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="last_id",
                description="ID of the last available object. New objects will go forward with respect to this ID",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="count",
                description="Number of new objects to return",
                required=False,
                type=int,
            ),
        ],
    )
    def list(self: "OViewSetProtocol[M]", request: Request, *args, **kwargs) -> Response:  # noqa: A003, ARG002
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
        first_id: str | None = request.query_params.get("first_id", None)
        # Used when navigating forward
        last_id: str | None = request.query_params.get("last_id", None)
        count: str = request.query_params.get("count", "50")

        if self.serializer_class is None:
            return Error(
                error_code=codes.internal_server_error,
                eng_description="Serializer class is not specified",
                ui_description="Serializer class is not specified",
            ).serialize_response()

        queryset: QuerySet[M] | Error = self.get_queryset()
        if isinstance(queryset, Error):
            return queryset.serialize_response()

        if hasattr(self, "filter_backends"):
            for backend in list(self.filter_backends):
                queryset = backend().filter_queryset(request, queryset, self)

        assert isinstance(queryset, QuerySetAny)

        queryset = queryset.order_by("pk")
        result = paginate_queryset(queryset, first_id, last_id, count)
        if isinstance(result, Error):
            return result.serialize_response()

        queryset, available_count, filtered_count = result

        queryset = prefetch(queryset, self.serializer_class, context=context)

        if isinstance(queryset, Error):
            return queryset.serialize_response()

        serializer = self.serializer_class(queryset, many=True, context=context)
        return Response(
            serializer.data,
            headers={
                "X-ODEVLIB-HAS-MORE": str(filtered_count < available_count).lower(),
            },
        )


class ORetrieveMixin(Generic[M]):
    """
    Provides retrieve method for OViewSet.
    """

    def retrieve(self: "OViewSetProtocol[M]", request: Request, *args, **kwargs) -> Response:  # noqa: ARG002
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

    def update(self: "OViewSetProtocol[M]", request: Request, *args, **kwargs) -> Response:  # noqa: ARG002
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
            serializer = self.update_serializer_class(instance, data=request.data, partial=partial, context=context)
        else:
            if self.create_serializer_class is None:
                return Error(
                    error_code=codes.internal_server_error,
                    eng_description="Create serializer class is not specified",
                    ui_description="Create serializer class is not specified",
                ).serialize_response()
            serializer = self.create_serializer_class(instance, data=request.data, partial=partial, context=context)

        serializer.is_valid(raise_exception=True)
        instance = self.perform_update(serializer)
        if isinstance(instance, Error):
            return instance.serialize_response()

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to forcibly invalidate the prefetch cache
            # on the instance to re-fetch updated data from the database.
            instance._prefetched_objects_cache = {}  # type: ignore[attr-defined]  # noqa: SLF001

        response_context = {
            "additional_kwargs": additional_kwargs,
            "user": request.user,
            "request": request,
            "action": "retrieve",
        }

        response_serializer = self.serializer_class(instance, context=response_context)
        return Response(response_serializer.data)

    def perform_update(self, serializer: ModelSerializer[M]) -> M | Error:
        """
        Hook for custom update logic.
        """
        try:
            return serializer.save()
        except Exception as e:
            return Error(
                error_code=codes.internal_server_error,
                eng_description=f"Error while updating object: {e}",
                ui_description="Error while updating object",
            )

    def partial_update(self: "OViewSetProtocol[M]", request: Request, *args, **kwargs) -> Response:
        kwargs["partial"] = True
        # TODO: fix this type ignore. Self should be annotated with both OViewSetProtocol and OUpdateMixin.
        # But with Python type system it's impossible to express that.
        return self.update(request, *args, **kwargs)  # type: ignore[attr-defined]


class ODestroyMixin(Generic[M]):
    """
    Provides delete method for OViewSet.
    """

    def destroy(self: "OViewSetProtocol[M]", request: Request, *args, **kwargs) -> Response:  # noqa: ARG002
        instance = self.get_object()
        if isinstance(instance, Error):
            return instance.serialize_response()

        # Check RBAC permissions
        if self.use_rbac:
            permissions = get_complete_instance_rbac_roles(
                request.user,
                instance._meta.model,  # noqa: SLF001
                instance.pk,
            )
            if isinstance(permissions, Error):
                return permissions.serialize_response()

            all_permissions = merge_permissions(permissions)
            has_permission = (
                has_access_to_entire_model(all_permissions, instance._meta.model, "d") or request.user.is_superuser
            )
            if not has_permission:
                return Error(
                    error_code=codes.permission_denied,
                    eng_description="You do not have access to delete this object",
                    ui_description="You do not have access to delete this object",
                ).serialize_response()

        try:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            return Error(
                error_code=codes.protected_instance,
                eng_description="This instance has protected relations with other instances. Delete related first",
                ui_description="This instance has protected relations with other instances. Delete related first",
            ).serialize_response()

    def perform_destroy(self, instance: M) -> None:
        """
        Hook for custom destroy logic.
        """
        instance.delete()


class ORelationsMixin(Generic[M]):
    # noinspection PyProtectedMember
    @extend_schema(
        summary="Get a list of relations with other objects",
        request=None,
        responses={200: RelationSerializer(many=True)},
    )
    @action(["GET"], detail=True)
    def relations(self: "OViewSetProtocol[M]", request: Request, *args, **kwargs) -> Response:  # noqa: ARG002
        # noinspection PyUnresolvedReferences
        instance = self.get_object()
        if isinstance(instance, Error):
            return instance.serialize_response()

        # Check RBAC permissions
        if self.use_rbac:
            permissions = get_complete_instance_rbac_roles(request.user, instance.__class__, instance.pk)
            if isinstance(permissions, Error):
                return permissions.serialize_response()

            all_permissions = merge_permissions(permissions)
            has_permission = (
                has_access_to_entire_model(all_permissions, instance.__class__, "r") or request.user.is_superuser
            )
            if not has_permission:
                return Error(
                    error_code=codes.permission_denied,
                    eng_description="You do not have access to get this model relations",
                    ui_description="You do not have access to get this model relations",
                ).serialize_response()

        result = get_relations(instance)
        response_serializer = RelationSerializer(data=result, many=True)
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data)


class OModelMixins(OCreateMixin[M], OUpdateMixin[M], OListMixin[M], ORetrieveMixin[M], ODestroyMixin[M]):
    """
    Contains all model methods in a single mixin for easy import.
    """
