from functools import cache
from django.db import models
from django.apps import apps
from django.core.exceptions import ValidationError


# Store a cache of all Django models here.
# This code will be evaluated on startup and will not be executed again.

@cache
def get_model_names() -> list[str]:
    _model_names: list[str] = [f"{model._meta.app_label}__{model._meta.model_name}" for model in apps.get_models()]
    print('model names: ', _model_names)
    return _model_names


class RBACModelField(models.CharField):
    """
    Field for storing RBAC model name.
    """

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 255
        super().__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        # Perform additional value validation here
        if not value in get_model_names():
            raise ValidationError("Value is not formatted correctly or model with given name does not exist")

        # Call the parent's validate method for basic CharField validation
        super().validate(value, model_instance)
