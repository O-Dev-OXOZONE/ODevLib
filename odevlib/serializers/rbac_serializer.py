import copy
import logging
import traceback
import typing
from collections import OrderedDict
from typing import TYPE_CHECKING

from django.db import models
from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework.fields import Field
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.settings import api_settings
from rest_framework.utils import model_meta

from odevlib.business_logic.rbac.permissions import (
    get_allowed_model_fields,
    get_complete_instance_rbac_roles,
    get_complete_rbac_roles,
    get_direct_rbac_roles,
    get_instance_rbac_roles,
    has_access_to_entire_model,
    has_access_to_model_field,
    merge_permissions,
)
from odevlib.errors import codes
from odevlib.middleware import get_user
from odevlib.models.errors import Error
from odevlib.models.rbac.mixins import RBACHierarchyModelMixin
from odevlib.serializers.omodelserializer import OModelCreateSerializer, OModelSerializer

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

_Base = serializers.ModelSerializer if TYPE_CHECKING else object

# List of fields which are always available regardless of the role. By default, this includes only
# 'id' field.
always_available_fields = ["id"]

action_to_mode_mapping = {
    "create": "c",
    "list": "r",
    "retrieve": "r",
    "update": "u",
    "partial_update": "u",
    "destroy": "d",
}


# TODO: deal with type ignore
class RBACSerializerMixin(_Base):
    def get_pk(self) -> int | None:
        if self.context["action"] in ["list"]:
            # In list action, we get sequence of instances, so we pick the first one and base our
            # field selection only on the first instance.
            #
            # This logic assumes that all instances are of the same type, that we have filtered our
            # queryset to only return instances available to user, and that all instances of
            # queryset has the same set of available fields.
            # assert self.instance is not None
            if self.instance is None:
                return None
            first = self.instance[0]
            if first is None:
                # In case of empty queryset, we don't have pk to return.
                return None
            pk = first.pk

        elif self.context["action"] in ["retrieve"]:
            assert self.instance is not None
            pk = self.instance.pk

        elif self.context["action"] in ["update", "partial_update"]:
            assert self.instance is not None
            pk = self.initial_data["pk"]

        elif self.context["action"] in ["create"]:
            # In case of creation, we don't have pk yet.
            return None
        else:
            msg = f"Unknown action {self.context['action']} in RBACSerializer"
            raise APIException(msg)
        return pk

    def filter_fields(self, fields: OrderedDict[str, Field]) -> OrderedDict[str, Field]:
        user: AbstractUser | None = get_user()
        if user is None:
            # This should never happen, as even unauthorized users have AnonymousUser instance.
            msg = f"Couldn't obtain user in {self.__class__.__name__}"
            raise APIException(msg)

        # We require context, as it contains action and we can't get fields without knowing
        # what are we getting fields for.
        if self.context is None or "action" not in self.context:
            Error(
                error_code=codes.internal_server_error,
                eng_description="Action was not passed to RBACSerializer .get_fields()",
                ui_description="Action was not passed to RBACSerializer .get_fields()",
            ).save()
            return fields

        # Give full access to all fields to superusers
        if user.is_superuser:
            return fields

        model: type[models.Model] = self.Meta.model
        model_name = f"{model._meta.app_label}__{model._meta.model_name}"  # noqa: SLF001

        mode: str = action_to_mode_mapping[self.context["action"]]

        if self.instance is None:
            # Prefetching is using this serializer, so we don't have a particular instance.
            instance = None
        elif self.context["action"] == "create":
            # In case of creation, we don't have an instance yet.
            instance = None
        elif self.context["action"] == "list":
            # In case of list, we have a list of instances, so we pick the first one and base our
            # field selection only on the first instance.
            instance = self.instance[0]
        else:
            # Update and retrieve actions have a single instance, use it.
            instance = self.instance

        # Global permissions are used in cases when we do not have access to the instance.
        global_permissions = merge_permissions(get_complete_rbac_roles(user))

        # Short-circuit if we have access to the entire model globally. No further checks are needed.
        if has_access_to_entire_model(global_permissions, model, mode):
            # logging.warning("Has access to entire model")
            return fields

        globally_available_fields = OrderedDict(
            [
                (field_name, field)
                for field_name, field in fields.items()
                if field_name in always_available_fields
                or has_access_to_model_field(global_permissions, model, field_name, mode)
            ],
        )

        # TODO: check if self.Meta.model works correctly (we don't need additional .__class__ here)
        has_inheritance = issubclass(model, RBACHierarchyModelMixin)

        # logging.warning(f"model: {model._meta.app_label}.{model._meta.model_name}")
        # logging.warning(f"All fields: {[k for k in fields.keys()]}")
        # logging.warning(f"Global permissions: {global_permissions}")
        # logging.warning(f"globally available fields: {globally_available_fields}")
        # logging.warning(f"has_inheritance: {has_inheritance}")
        # logging.warning(f"instance: {instance}")
        # logging.warning(f"instance.pk: {instance.pk if instance is not None else None}")

        # If we do not have an instance yet, use parent model to get user roles.
        if instance is None:
            if not has_inheritance:
                # logging.warning("Has no inheritance :(")
                # If we don't even have a parent, return permissions based on global roles only.
                return globally_available_fields

            # We have a parent, use it.
            roles = get_direct_rbac_roles(user)
            assert issubclass(model, RBACHierarchyModelMixin)
            parent_model = self.Meta.model.get_rbac_parent_model()
            assert issubclass(parent_model, models.Model)
            # TODO: what to do if we do not have parent field and use query parameter instead?
            parent_field_name = parent_model.get_rbac_parent_field_name()
            assert isinstance(parent_field_name, str)
            parent_pk = self.data.get(parent_field_name, None)
            if parent_pk is None:
                # If we don't have parent pk, fall back to global permissions.
                return globally_available_fields
            instance_level_parent_permissions = merge_permissions(
                get_complete_instance_rbac_roles(user, parent_model, parent_pk),
            )

            allowed_fields = get_allowed_model_fields(
                permissions=instance_level_parent_permissions,
                model=model_name,
                mode=mode,
            )
            return OrderedDict(
                [
                    (field_name, field)
                    for field_name, field in fields.items()
                    if field_name in always_available_fields or field_name in allowed_fields
                ],
            )

        # roles = get_direct_rbac_roles(user)
        roles = get_complete_instance_rbac_roles(user, model, instance.pk)
        if isinstance(roles, Error):
            return fields

        permissions = merge_permissions(roles)

        if model_name in permissions:
            return fields

        allowed_fields = get_allowed_model_fields(
            permissions=permissions,
            model=model_name,
            mode=mode,
        )
        return OrderedDict(
            [
                (field_name, field)
                for field_name, field in fields.items()
                if field_name in always_available_fields or field_name in allowed_fields
            ],
        )

    def get_fields(self) -> dict[str, Field]:
        """
        Return the dict of field names -> field instances that should be
        used for `self.fields` when instantiating the serializer.

        Default mode is '_' to block all modes. Allowed ones are 'c', 'r', 'u' and 'd'.
        """
        if self.url_field_name is None:
            self.url_field_name = api_settings.URL_FIELD_NAME

        assert hasattr(self, "Meta"), 'Class {self.__class__.__name__} missing "Meta" attribute'
        assert hasattr(self.Meta, "model"), 'Class {self.__class__.__name__} missing "Meta.model" attribute'

        if model_meta.is_abstract_model(self.Meta.model):
            msg = "Cannot use ModelSerializer with Abstract Models."
            raise ValueError(msg)

        declared_fields: OrderedDict[str, Field] = copy.deepcopy(self._declared_fields)
        model: type[models.Model] = self.Meta.model
        depth = getattr(self.Meta, "depth", 0)

        assert isinstance(depth, int), "'depth' must be an integer."
        if depth is not None:
            assert depth >= 0, "'depth' may not be negative."
            assert depth <= 10, "'depth' may not be greater than 10."

        # Retrieve metadata about fields & relationships on the model class.
        model_field_info = model_meta.get_field_info(model)
        model_field_names = self.get_field_names(declared_fields, model_field_info)

        # Determine any extra field arguments and hidden fields that should be included
        extra_kwargs = self.get_extra_kwargs()
        extra_kwargs, hidden_fields = self.get_uniqueness_extra_kwargs(
            model_field_names,
            declared_fields,
            extra_kwargs,
        )

        # Determine all possible fields that may be included on the serializer.
        fields: typing.OrderedDict[str, Field] = OrderedDict()

        for field_name in model_field_names:
            # If the field is explicitly declared on the class then use that.
            if field_name in declared_fields:
                fields[field_name] = declared_fields[field_name]
                continue

            extra_field_kwargs = extra_kwargs.get(field_name, {})
            # TODO: remove support for "*", checking that no code uses this pattern
            source = extra_field_kwargs.get("source", "*")
            if source == "*":
                source = field_name

            # Determine the serializer field class and keyword arguments.
            field_class, field_kwargs = self.build_field(source, model_field_info, model, depth)

            # Include any kwargs defined in `Meta.extra_kwargs`
            field_kwargs = self.include_extra_kwargs(field_kwargs, extra_field_kwargs)

            # Create the serializer field.
            fields[field_name] = field_class(**field_kwargs)

        # Add in any hidden fields.
        fields.update(hidden_fields)

        return self.filter_fields(fields)


class RBACCreateSerializerMixin(_Base):
    def create(self, validated_data):
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
        raise_errors_on_nested_writes("create", self, validated_data)

        save_kwargs = {}
        additional_kwargs = self.context.get("additional_kwargs", {})
        for key, value in additional_kwargs.items():
            save_kwargs[key] = value
        save_kwargs["user"] = self.context["user"]

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
        except TypeError as e:
            tb = traceback.format_exc()
            msg = (
                f"Got a `TypeError` when calling `{ModelClass.__name__}.{ModelClass._default_manager.name}.create()`. "
                "This may be because you have a writable field on the "
                "serializer class that is not a valid argument to "
                f"`{ModelClass.__name__}.{ModelClass._default_manager.name}.create()`. You may need to make the field "
                f"read-only, or override the {self.__class__.__name__}.create() method to handle "
                f"this correctly.\nOriginal exception was:\n {tb}"
            )
            raise TypeError(msg) from e

        # Save many-to-many relationships after the instance is created.
        if many_to_many:
            for field_name, value in many_to_many.items():
                field = getattr(instance, field_name)
                field.set(value)

        return instance

    def update(self, instance: models.Model, validated_data):
        save_kwargs = {}
        for key, value in self.context.get("additional_kwargs", {}).items():
            save_kwargs[key] = value
        save_kwargs["user"] = self.context["user"]

        raise_errors_on_nested_writes("update", self, validated_data)

        # get_field_info has incorrect type annotations in the stub, so we have to ignore the type :c
        info = model_meta.get_field_info(instance)

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


class RBACSerializer(RBACSerializerMixin, serializers.ModelSerializer):
    pass


class RBACOSerializer(RBACSerializerMixin, OModelSerializer):
    pass


class RBACCreateSerializer(RBACSerializerMixin, serializers.ModelSerializer):
    pass


class RBACOCreateSerializer(RBACSerializerMixin, OModelCreateSerializer):
    pass
