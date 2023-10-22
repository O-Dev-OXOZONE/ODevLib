import traceback
from typing import ClassVar

from django.db.models import Model
from rest_framework.fields import empty
from rest_framework.serializers import ModelSerializer, raise_errors_on_nested_writes
from rest_framework.utils import model_meta


class OModelSerializer(ModelSerializer):
    """
    You can also add "prefetch_related_fields": List[str] to the Meta class to automatically prefetch fields in case
    some SerializerMethodFields use access to other fields.
    """

    class Meta:
        # Tuple may be used to specify particular fields to be used.
        # "__all__" string may be used to include all discovered fields.
        fields: tuple[str, ...] = (
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        )


class OModelCreateSerializer(ModelSerializer):
    class Meta:
        model: type[Model]
        # Tuple may be used to specify particular fields to be used.
        # "__all__" string may be used to include all discovered fields.
        fields: tuple[str, ...] = ()
        custom_validation_errors: ClassVar[dict[str, dict[str, str]]] = {}

    def __init__(self, instance=None, data=empty, **kwargs):
        super().__init__(instance, data, **kwargs)
        if hasattr(self.Meta, 'custom_validation_errors'):
            for field, errors in self.Meta.custom_validation_errors.items():  # ability to rewrite default errors
                for err_type, msg in errors.items(): self.fields[field].error_messages[err_type] = msg

    def get_additional_kwargs(self):
        return self.context.get('additional_kwargs', dict())

    def create(self, validated_data):
        save_kwargs = {}
        additional_kwargs = self.get_additional_kwargs()
        for key, value in additional_kwargs.items():
            save_kwargs[key] = value
        save_kwargs['user'] = self.context['user']

        """
        We have a bit of extra checking around this in order to provide
        descriptive messages when something goes wrong, but this method is
        essentially just:

            return ExampleModel.objects.create(**validated_data)

        If there are many to many fields present on the instance then they
        cannot be set until the model is instantiated, in which case the
        implementation is like so:

            example_relationship = validated_data.pop('example_relationship')
            instance = ExampleModel.objects.create(**validated_data)
            instance.example_relationship = example_relationship
            return instance

        The default implementation also does not handle nested relationships.
        If you want to support writable nested relationships you'll need
        to write an explicit `.create()` method.
        """
        raise_errors_on_nested_writes('create', self, validated_data)

        ModelClass = self.Meta.model

        # Remove many-to-many relationships from validated_data.
        # They are not valid arguments to the default `.create()` method,
        # as they require that the instance has already been saved.
        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        try:
            instance = ModelClass(**validated_data, **additional_kwargs)
            instance.save(force_insert=True, **save_kwargs)
        except TypeError:
            tb = traceback.format_exc()
            msg = (
                    'Got a `TypeError` when calling `%s.%s.create()`. '
                    'This may be because you have a writable field on the '
                    'serializer class that is not a valid argument to '
                    '`%s.%s.create()`. You may need to make the field '
                    'read-only, or override the %s.create() method to handle '
                    'this correctly.\nOriginal exception was:\n %s' %
                    (
                        ModelClass.__name__,
                        ModelClass._default_manager.name,
                        ModelClass.__name__,
                        ModelClass._default_manager.name,
                        self.__class__.__name__,
                        tb
                    )
            )
            raise TypeError(msg)

        # Save many-to-many relationships after the instance is created.
        if many_to_many:
            for field_name, value in many_to_many.items():
                field = getattr(instance, field_name)
                field.set(value)

        return instance

    def update(self, instance: Model, validated_data):
        save_kwargs = {}
        for key, value in self.get_additional_kwargs().items():
            save_kwargs[key] = value
        save_kwargs['user'] = self.context['user']

        raise_errors_on_nested_writes('update', self, validated_data)

        info = model_meta.get_field_info(instance)  # type: ignore

        # Simply set each attribute on the instance, and then save it.
        # Note that unlike `.create()` we don't need to treat many-to-many
        # relationships as being a special case. During updates we already
        # have an instance pk for the relationships to be associated with.
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)

        instance.save(**save_kwargs)

        # Note that many-to-many fields are set after updating instance.
        # Setting m2m fields triggers signals which could potentially change
        # updated instance and we do not want it to collide with .update()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)

        return instance
