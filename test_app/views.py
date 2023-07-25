from test_app.models import ExampleOModel
from test_app.serializers import ExampleOModelCreateSerializer, ExampleOModelSerializer

from odevlib.views.oviewset import OModelViewSet


class ExampleOModelViewSet(OModelViewSet[ExampleOModel]):
    queryset = ExampleOModel.objects.all()
    serializer_class = ExampleOModelSerializer
    create_serializer_class = ExampleOModelCreateSerializer
