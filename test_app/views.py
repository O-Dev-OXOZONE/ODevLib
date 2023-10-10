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


class ExampleRBACChildViewSet(OModelViewSet[ExampleRBACChild]):
    queryset = ExampleRBACChild.objects.all()
    serializer_class = ExampleRBACChildSerializer
    create_serializer_class = ExampleRBACChildCreateSerializer
    use_rbac = True
