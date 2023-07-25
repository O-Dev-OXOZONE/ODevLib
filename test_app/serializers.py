from odevlib.serializers import OModelSerializer, OModelCreateSerializer
from rest_framework import serializers

from test_app.models import ExampleOModel


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
        fields = OModelCreateSerializer.Meta.fields + (
            "test_field",
        )
