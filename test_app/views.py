from django.contrib.auth.base_user import AbstractBaseUser
from django.db.models import Q, QuerySet
from django_filters.rest_framework import DjangoFilterBackend

from odevlib.models.errors import Error
from odevlib.models.rbac.instance_role_assignment import InstanceRoleAssignment
from odevlib.models.rbac.role_assignment import RoleAssignment
from odevlib.views.mixins import OCursorPaginatedListMixin
from odevlib.views.oviewset import OModelViewSet, OViewSet
from test_app.models import ExampleOModel, ExampleRBACChild, ExampleRBACParent
from test_app.serializers import (
    ExampleOModelCreateSerializer,
    ExampleOModelSerializer,
    ExampleRBACChildCreateSerializer,
    ExampleRBACChildSerializer,
    ExampleRBACParentCreateSerializer,
    ExampleRBACParentSerializer,
)


class ExampleOModelViewSet(OModelViewSet[ExampleOModel]):
    queryset = ExampleOModel.objects.all()
    serializer_class = ExampleOModelSerializer
    create_serializer_class = ExampleOModelCreateSerializer


class PaginatedExampleOModelViewSet(OViewSet[ExampleOModel], OCursorPaginatedListMixin[ExampleOModel]):
    queryset = ExampleOModel.objects.all()
    serializer_class = ExampleOModelSerializer
    create_serializer_class = ExampleOModelCreateSerializer


class ExampleRBACParentViewSet(OModelViewSet[ExampleRBACParent]):
    queryset = ExampleRBACParent.objects.all()
    serializer_class = ExampleRBACParentSerializer
    create_serializer_class = ExampleRBACParentCreateSerializer
    use_rbac = True

    def get_queryset(self) -> QuerySet[ExampleRBACParent] | Error:
        assert isinstance(self.request.user, AbstractBaseUser)
        qs = super().get_queryset()

        if isinstance(qs, Error):
            return qs

        is_globally_available = RoleAssignment.objects.filter(
            user=self.request.user,
            role__permissions__has_key="test_app__examplerbacparent",
        ).exists()

        if is_globally_available:
            return qs

        available_ids = InstanceRoleAssignment.objects.filter(
            user=self.request.user,
            model="test_app__examplerbacparent",
        ).values_list("instance_id", flat=True)

        return qs.filter(id__in=available_ids)


class ExampleRBACChildViewSet(OModelViewSet[ExampleRBACChild]):
    queryset = ExampleRBACChild.objects.all()
    serializer_class = ExampleRBACChildSerializer
    create_serializer_class = ExampleRBACChildCreateSerializer
    use_rbac = True

    def get_queryset(self) -> QuerySet[ExampleRBACChild] | Error:
        assert isinstance(self.request.user, AbstractBaseUser)
        qs = super().get_queryset()

        if isinstance(qs, Error):
            return qs

        is_globally_available = RoleAssignment.objects.filter(
            user=self.request.user,
            role__permissions__has_key="test_app__examplerbacchild",
        ).exists()

        if is_globally_available:
            return qs

        available_ids = InstanceRoleAssignment.objects.filter(
            user=self.request.user,
            model="test_app__examplerbacchild",
        ).values_list("instance_id", flat=True)

        available_parent_ids = InstanceRoleAssignment.objects.filter(
            user=self.request.user,
            model="test_app__examplerbacparent",
        ).values_list("instance_id", flat=True)

        return qs.filter(Q(id__in=available_ids) | Q(parent_id__in=available_parent_ids))


class ExampleOModelFilteredViewSet(OViewSet, OCursorPaginatedListMixin):
    queryset = ExampleOModel.objects.all()
    serializer_class = ExampleOModelSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("test_field",)
