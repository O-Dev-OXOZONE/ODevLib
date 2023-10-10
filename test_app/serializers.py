from odevlib.serializers import OModelCreateSerializer, OModelSerializer
from odevlib.serializers.rbac_serializer import RBACOCreateSerializer, RBACOSerializer
from test_app.models import ExampleOModel, ExampleRBACChild, ExampleRBACParent


class ExampleOModelSerializer(OModelSerializer):
    class Meta:
        model = ExampleOModel
        fields = OModelSerializer.Meta.fields + (
            "id",
            "test_field",
        )


class ExampleOModelCreateSerializer(OModelCreateSerializer):
    class Meta:
        model = ExampleOModel
        fields = OModelCreateSerializer.Meta.fields + ("test_field",)


class ExampleRBACParentSerializer(RBACOSerializer):
    class Meta:
        model = ExampleRBACParent
        fields = (
            "id",
            "test_field",
            "test_field2",
        )


class ExampleRBACParentCreateSerializer(RBACOCreateSerializer):
    class Meta:
        model = ExampleRBACParent
        fields = (
            "test_field",
            "test_field2",
        )


class ExampleRBACChildSerializer(RBACOSerializer):
    class Meta:
        model = ExampleRBACChild
        fields = (
            "id",
            "parent",
            "test_field3",
            "test_field4",
        )


class ExampleRBACChildCreateSerializer(RBACOCreateSerializer):
    class Meta:
        model = ExampleRBACChild
        fields = (
            "parent",
            "test_field3",
            "test_field4",
        )
