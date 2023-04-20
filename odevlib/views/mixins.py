from django.db.models import ProtectedError
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from odevlib.errors import codes
from odevlib.models.errors import Error
from odevlib.business_logic.rbac.permissions import (
    get_complete_instance_user_roles,
    get_user_roles,
    has_access_to_entire_model,
    merge_permissions,
)
from odevlib.business_logic.relations import get_relations
from odevlib.prefetching import prefetch
from odevlib.serializers.related import RelationSerializer


# TODO: find how to gracefully handle mypy errors for mixins
class OCreateMixin:
    """
    Provides create method for OViewSet.
    """

    def create(self, request, *args, **kwargs):
        # Prepare additional kwargs, which contain non-pk URL lookup fields and profile of requester.
        additional_kwargs = kwargs.copy()  # type: ignore
        additional_kwargs.pop(self.lookup_url_kwarg, None)  # type: ignore
        context = {
            "additional_kwargs": additional_kwargs,
            "user": request.user,
            "request": request,
            "action": "create",
        }

        serializer = self.create_serializer_class(data=request.data, context=context)  # type: ignore

        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_serializer = self.serializer_class(instance)  # type: ignore
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class OListMixin:
    """
    Provides list method for OViewSet.
    """

    def list(self, request, *args, **kwargs):
        # Prepare additional kwargs, which contain non-pk URL lookup fields and profile of requester.
        additional_kwargs = kwargs.copy()
        additional_kwargs.pop(self.lookup_url_kwarg, None)  # type: ignore
        context = {
            "additional_kwargs": additional_kwargs,
            "user": request.user,
            "request": request,
            "action": "list",
        }

        queryset = prefetch(self.get_queryset(), self.serializer_class, context=context)  # type: ignore
        if hasattr(self, "filter_backends"):
            for backend in list(self.filter_backends):  # type: ignore
                queryset = backend().filter_queryset(self.request, queryset, self)  # type: ignore

        serializer = self.serializer_class(queryset, many=True, context=context)  # type: ignore
        return Response(serializer.data)


class ORetrieveMixin:
    """
    Provides retrieve method for OViewSet.
    """

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()  # type: ignore
        if isinstance(instance, Error):
            return instance.serialize_response()

        # Prepare additional kwargs, which contain non-pk URL lookup fields and profile of requester.
        additional_kwargs = kwargs.copy()
        additional_kwargs.pop(self.lookup_url_kwarg, None)  # type: ignore
        context = {
            "additional_kwargs": additional_kwargs,
            "user": request.user,
            "request": request,
            "action": "retrieve",
        }

        serializer = self.serializer_class(instance, context=context)  # type: ignore

        return Response(serializer.data)


class OUpdateMixin:
    """
    Provides put/patch methods for OViewSet.
    """

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()  # type: ignore
        if isinstance(instance, Error):
            return instance.serialize_response()

        # Prepare additional kwargs, which contain non-pk URL lookup fields and profile of requester.
        additional_kwargs = kwargs.copy()
        additional_kwargs.pop(self.lookup_url_kwarg, None)  # type: ignore
        context = {
            "additional_kwargs": additional_kwargs,
            "user": request.user,
            "request": request,
            "action": "update",
        }

        # Decide if dedicated update serializer should be used based on its presence in the viewset class
        if self.update_serializer_class is not None:  # type: ignore
            serializer = self.update_serializer_class(instance, data=request.data, partial=partial, context=context)  # type: ignore
        else:
            serializer = self.create_serializer_class(instance, data=request.data, partial=partial, context=context)  # type: ignore

        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to forcibly invalidate the prefetch cache on
            # the instance to re-fetch updated data from the database.
            instance._prefetched_objects_cache = {}

        response_context = {
            "additional_kwargs": additional_kwargs,
            "user": request.user,
            "request": request,
            "action": "retrieve",
        }

        response_serializer = self.serializer_class(instance, context=response_context)  # type: ignore
        return Response(response_serializer.data)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)


class ODestroyMixin:
    """
    Provides delete method for OViewSet.
    """

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()  # type: ignore
        if isinstance(instance, Error):
            return instance.serialize_response()

        # Check RBAC permissions
        if self.use_rbac:  # type: ignore
            all_permissions = merge_permissions(
                get_complete_instance_user_roles(
                    request.user,
                    instance,
                    instance.pk,
                ),
            )
            has_permission = has_access_to_entire_model(all_permissions, instance, "d") or request.user.is_superuser
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


class ORelationsMixin:
    # noinspection PyProtectedMember
    @extend_schema(
        summary="Получить список всех связей с другими объектами",
        request=None,
        responses={200: RelationSerializer(many=True)},
    )
    @action(["GET"], detail=True)
    def relations(self, request, *args, **kwargs):
        # noinspection PyUnresolvedReferences
        instance = self.get_object()  # type: ignore
        if isinstance(instance, Error):
            return instance.serialize_response()

        # Check RBAC permissions
        if self.use_rbac:  # type: ignore
            all_permissions = merge_permissions(get_complete_instance_user_roles(request.user, instance, instance.pk))
            has_permission = has_access_to_entire_model(all_permissions, instance, "r") or request.user.is_superuser
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


class OModelMixins(OCreateMixin, OUpdateMixin, OListMixin, ORetrieveMixin, ODestroyMixin):
    """
    Contains all model methods in a single mixin for easy import.
    """
