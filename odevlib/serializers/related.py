from rest_framework import serializers


class RelationSerializer(serializers.Serializer):
    model_name = serializers.CharField(label="Название модели")
    verbose_name = serializers.CharField(label="Название модели на русском")
    verbose_name_plural = serializers.CharField(label="Название модели на русском в множественном числе")
    related_field = serializers.CharField(label="Название поля в связанной модели")
    ids: serializers.ListSerializer[serializers.IntegerField] = serializers.ListSerializer(
        child=serializers.IntegerField()
    )
