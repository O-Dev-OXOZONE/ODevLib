import inspect
from typing import Any, Optional, Type, TypeVar, Union

from django.core.exceptions import FieldError
from django.db import models
from django.db.models import QuerySet
from django.db.models.fields.related_descriptors import (
    ForwardManyToOneDescriptor,
    ForwardOneToOneDescriptor,
    ManyToManyDescriptor,
    ReverseManyToOneDescriptor,
    ReverseOneToOneDescriptor,
)
from rest_framework.relations import HyperlinkedRelatedField, ManyRelatedField, RelatedField
from rest_framework.serializers import BaseSerializer, ListSerializer, ModelSerializer

SERIALIZER_SOURCE_RELATION_SEPARATOR = "."


T = TypeVar("T", bound=models.Model)


# TODO: fix type ignores here
def prefetch(
    queryset: QuerySet[T],
    serializer: Type[ModelSerializer],
    *,
    excluded_fields=None,
    extra_select_fields=None,
    extra_prefetch_fields=None,
    context: Optional[dict[str, Any]] = None,
) -> QuerySet[T]:
    if not isinstance(excluded_fields, (set, list)) and excluded_fields is not None:
        raise TypeError(f"excluded_fields must be a list or a set if supplied. Received {type(excluded_fields)}")

    if not isinstance(extra_select_fields, (set, list)) and extra_select_fields is not None:
        raise TypeError(
            f"extra_select_fields must be a list or a set if supplied. Received {type(extra_select_fields)}"
        )

    if not isinstance(extra_prefetch_fields, (set, list)) and extra_prefetch_fields is not None:
        raise TypeError(
            f"extra_prefetch_fields must be a list or a set if supplied. Received {type(extra_prefetch_fields)}"
        )

    excluded_fields = set() if excluded_fields is None else set(excluded_fields)
    extra_select_fields = set() if extra_select_fields is None else set(extra_select_fields)
    extra_prefetch_fields = set() if extra_prefetch_fields is None else set(extra_prefetch_fields)

    select_related, prefetch_related = _prefetch(serializer, context=context)
    select_related = (select_related | extra_select_fields) - excluded_fields
    prefetch_related = (prefetch_related | extra_prefetch_fields) - excluded_fields

    select_related = [s.replace(".", "__") for s in select_related]
    prefetch_related = [s.replace(".", "__") for s in prefetch_related]

    try:
        if select_related:
            queryset = queryset.select_related(*select_related)
        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)
        return queryset
    except FieldError as e:
        raise ValueError(
            f"Calculated wrong field in select_related. Do you have a nested serializer for a ForeignKey where "
            f"you've forgotten to specify many=True? Original error: {e}"
        )


def _prefetch(
    serializer: Union[Type[BaseSerializer], BaseSerializer],
    path=None,
    indentation=0,
    context: Optional[dict[str, Any]] = None,
):
    """
    Returns prefetch_related, select_related
    :param serializer:
    :return:
    """
    prepend = f"{path}__" if path is not None else ""
    # class_name = getattr(serializer, "__name__", serializer.__class__.__name__)
    # logger.debug("\n")

    # logger.debug(f'{" " * indentation}LOOKING AT SERIALIZER: {class_name} from path: {prepend}')

    select_related = set()
    prefetch_related = set()

    if inspect.isclass(serializer):
        serializer_instance = serializer(context=context)
    else:
        serializer_instance = serializer

    if hasattr(serializer_instance, "Meta") and hasattr(serializer_instance.Meta, "prefetch_related_fields"):
        for s in serializer_instance.Meta.prefetch_related_fields:
            prefetch_related.add(prepend + s)

    # For some fucking reason _prefetch does not go inside the child serializer, so special case handling
    # is required here.
    if isinstance(serializer_instance, (ListSerializer, ManyRelatedField)):
        if hasattr(serializer_instance.child, "Meta") and hasattr(  # type: ignore
            serializer_instance.child.Meta, "prefetch_related_fields"  # type: ignore
        ):
            for s in serializer_instance.child.Meta.prefetch_related_fields:  # type: ignore
                prefetch_related.add(prepend + s)

    try:
        fields = getattr(serializer_instance, "child", serializer_instance).fields.fields.items()
    except AttributeError:
        # This can happen if there's no further fields, e.g. if we're passed a PrimaryKeyRelatedField
        # as the nested representation of a ManyToManyField
        return set(), set()

    for name, field_instance in fields:
        # field_type_name = field_instance.__class__.__name__
        # logger.debug(f'{" " * indentation} Field "{name}", type: {field_type_name}, src: "{field_instance.source}"')

        attribute_type = hasattr(serializer, "Meta") and type(getattr(serializer.Meta.model, name, None))
        # We potentially need to recurse deeper
        if (
            isinstance(field_instance, (BaseSerializer, RelatedField, ManyRelatedField))
            and (not isinstance(field_instance, IGNORED_FIELD_TYPES))
            and (
                attribute_type is not property
                or any(
                    attribute_type is descriptor
                    for descriptor in (
                        ForwardManyToOneDescriptor,
                        ForwardOneToOneDescriptor,
                        ReverseOneToOneDescriptor,
                        ReverseManyToOneDescriptor,
                        ManyToManyDescriptor,
                    )
                )
            )
        ):
            # logger.debug(f'{" " * indentation}Found related: {field_type_name} ({type(field_instance)}) - recursing deeper')
            field_path = f"{prepend}{field_instance.source}"

            # Fields where the field name *is* the model.
            if isinstance(field_instance, RelatedField):
                # logger.debug(f'{" " * indentation} Found related field: {field_type_name} - selecting {field_instance.source}')
                select_related.add(f"{prepend}{field_instance.source}")

                """
                If we have multiple entities, we need to use prefetch_related instead of select_related
                We also need to do this for all further calls
                """
            elif isinstance(field_instance, (ListSerializer, ManyRelatedField)):
                # logger.debug(f'{" " * indentation} Found *:m relation: {field_type_name}')
                prefetch_related.add(field_path)

                # If it's a ManyRelatedField, we can only get the actual underlying field by querying child_relation
                nested_field = getattr(field_instance, "child_relation", field_instance)

                select, prefetch = _prefetch(nested_field, field_path, indentation + 4)  # type: ignore
                prefetch_related |= select
                prefetch_related |= prefetch
            else:
                # logger.debug(f'{" " * indentation} Found *:1 relation: {field_type_name}')
                select_related.add(field_path)
                select, prefetch = _prefetch(field_instance, field_path, indentation + 4)
                select_related |= select
                prefetch_related |= prefetch

        elif SERIALIZER_SOURCE_RELATION_SEPARATOR in field_instance.source:
            # The serializer declares a field from a related object.
            relation_name = field_instance.source.split(SERIALIZER_SOURCE_RELATION_SEPARATOR)[0]
            if hasattr(serializer, "Meta") and is_model_relation(serializer.Meta.model, relation_name):
                # logger.debug(f'{" " * indentation} Found *:1 relation: {relation_name}')
                select_related.add(prepend + relation_name)

    return select_related, prefetch_related


def is_model_relation(model, field_name):
    field = next((field for field in model._meta.fields if field.name == field_name), None)
    return isinstance(field, models.ForeignKey) or isinstance(field, models.OneToOneField)


IGNORED_FIELD_TYPES = (
    # This is a subclass of RelatedField, but it always generates a URL no matter the depth, so we shouldn't prefetch
    # based on it.
    HyperlinkedRelatedField
)
