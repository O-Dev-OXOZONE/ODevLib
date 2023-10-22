import inspect
from collections.abc import Callable, Sequence
from typing import (
    ClassVar,
    Generic,
    Protocol,
    TypeVar,
)

from django.db.models import Model, QuerySet
from django_stubs_ext import QuerySetAny
from drf_spectacular.utils import OpenApiParameter
from rest_framework import serializers
from rest_framework.permissions import (
    BasePermission,
    OperandHolder,
    SingleOperandHolder,
)
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin

from odevlib.errors import codes
from odevlib.models.errors import Error
from odevlib.views import OModelMixins

T = TypeVar("T", bound=Model)


class OViewSetProtocol(Protocol, Generic[T]):
    """
    Protocol used to ensure that OViewSet has all necessary fields.
    """

    # SERIALIZERS SECTION #
    @property
    def serializer_class(self) -> type[serializers.ModelSerializer[T]] | None:
        ...

    create_serializer_class: type[serializers.ModelSerializer[T]] | None
    update_serializer_class: type[serializers.ModelSerializer[T]] | None

    # URL SECTION #
    # Name of the main lookup kwarg used in the URL. Used for retrieve/put/patch methods.
    lookup_url_kwarg: str

    additional_query_parameters: dict[str, list[OpenApiParameter]]

    # You can override these fields to add prefetch/select related fields to the query to get rid of N+1 problem.
    prefetch_related_fields: list[str]
    select_related_fields: list[str]

    # Permission setup
    use_rbac: bool

    def filter_by_kwargs(self, queryset: QuerySet[T], kwargs: dict) -> QuerySet[T]:
        ...

    def get_queryset(self) -> QuerySet[T] | Error:
        ...

    def get_object(self) -> T | Error:
        ...

    def perform_create(self, serializer: serializers.ModelSerializer[T]) -> T | Error:
        ...

    def perform_update(self, serializer: serializers.ModelSerializer[T]) -> T | Error:
        ...

    def perform_destroy(self, instance: T) -> None:
        ...


class OViewSet(ViewSetMixin, APIView, Generic[T]):
    """
    Implements ODevLib custom opinionated ViewSet. It includes:
      - Support for multiple query parameters.
      - Support for ODevLib permission system.

    To use this ViewSet, you need to specify:
      - serializer_class — this serializer is used in all endpoint response bodies.
      - create_serializer_class — this serializer is used in post endpoint request bodies, plus in put/patch request
        bodies, if create_serializer_class is not specified.
      - update_serializer_class — this serializer is used in put/patch endpoint request bodies, if specified.

      - queryset — queryset used to interact with database. Data is saved there and obtained from there.

      - permission_subsystem — any ODevLib ViewSet should have permission subsystem specified. Presence of this field
        ensures that no data leak sources are explicitly present in the system, hardening the security of the system.

    You can include additional kwargs in the path. They are automatically passed to serializer context under the
    additional_kwargs key. OModelSerializer uses them to automatically set model fields to the corresponding values.
    I.e. you can use them to create nested model hierarchies, where innermost entities will be limited to outer models
    as their parents.
    """

    # SERIALIZERS SECTION #
    serializer_class: type[serializers.ModelSerializer[T]] | None = None
    create_serializer_class: type[serializers.ModelSerializer[T]] | None = None
    update_serializer_class: type[serializers.ModelSerializer[T]] | None = None

    # DATABASE INTERACTION SECTION #
    queryset: QuerySet[T] | None = None

    # URL SECTION #
    # Name of the main lookup kwarg used in the URL. Used for retrieve/put/patch methods.
    lookup_url_kwarg = "pk"

    additional_query_parameters: ClassVar[dict[str, list[OpenApiParameter]]] = {
        "list": [],
        "retrieve": [],
        "update": [],
        "partial_update": [],
        "create": [],
        "destroy": [],
    }

    # You can override these fields to add prefetch/select related fields to the query to get rid of N+1 problem.
    prefetch_related_fields: tuple[str, ...] = ()
    select_related_fields: tuple[str, ...] = ()

    # Permission setup
    use_rbac: bool = False
    permission_classes: Sequence[  # type: ignore
        Callable[[], BasePermission] | type[BasePermission] | OperandHolder | SingleOperandHolder
    ]

    def __init__(self, *args, **kwargs) -> None:  # noqa: ARG002
        super().__init__()
        from odevlib.schema.oautoschema import OAutoSchema

        for method in [
            "create",
            "list",
            "retrieve",
            "update",
            "partial_update",
            "destroy",
        ]:
            if hasattr(self, method):
                m = getattr(self.__class__, method)
                # Ignore actions that have custom schema set (i.e. with @extend_schema).
                if hasattr(m, "kwargs") and "schema" in m.kwargs:
                    continue
                m.kwargs = {"schema": OAutoSchema}

    def filter_by_kwargs(self, queryset: QuerySet[T], kwargs: dict) -> QuerySet[T]:  # noqa: ARG002
        """
        If several URL arguments are present, you may use this method to filter queryset by the additional kwargs.
        """
        return queryset

    def get_queryset(self) -> QuerySet[T] | Error:
        """
        Get the list of items for this view.
        This must be an iterable, and may be a queryset.
        Defaults to using `self.queryset`.

        This method should always be used rather than accessing `self.queryset`
        directly, as `self.queryset` gets evaluated only once, and those results
        are cached for all subsequent requests.

        You may want to override this if you need to provide different
        querysets depending on the incoming request.

        (E.g. return a list of items that is specific to the user)
        """
        assert self.queryset is not None, (
            f"'{self.__class__.__name__}' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
        )

        if not hasattr(self, "kwargs"):
            # Handle Swagger schema generation. When Swagger schema is generated, no request/kwargs are present.
            return self.queryset.none()

        queryset = self.filter_by_kwargs(self.queryset, self.kwargs)
        if isinstance(queryset, QuerySetAny):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()

        if self.prefetch_related_fields != []:
            queryset = queryset.prefetch_related(*self.prefetch_related_fields)

        if self.select_related_fields != []:
            queryset = queryset.select_related(*self.select_related_fields)

        return queryset

    def get_object(self) -> T | Error:
        """
        Return the object the view is displaying.
        """
        queryset = self.get_queryset()
        if isinstance(queryset, Error):
            return queryset

        # Ensure lookup field is present in URL query params (which is automatically parsed into kwargs).
        assert self.lookup_url_kwarg in self.kwargs, (
            f"Expected view {self.__class__.__name__} to be called with a URL keyword argument "
            f'named "{self.lookup_url_kwarg}". Fix your URL conf, or set the `.lookup_field` '
            "attribute on the view correctly."
        )

        # Get and return object, raising error if necessary.
        pk = self.kwargs[self.lookup_url_kwarg]

        try:
            return queryset.get(**{self.lookup_url_kwarg: pk})
        except queryset.model.DoesNotExist:
            # Disable _meta access warning.
            # noinspection PyProtectedMember
            return Error(
                error_code=codes.does_not_exist,
                eng_description=f"{inspect.getmro(queryset.model)[0].__name__} instance with pk={pk} does not exist",
                ui_description=f"{queryset.model._meta.verbose_name} with pk={pk} does not exist",  # noqa: SLF001
            )


class OModelViewSet(OModelMixins[T], OViewSet[T]):
    """
    Contains OViewSet and all model mixins for easy importing.
    """
