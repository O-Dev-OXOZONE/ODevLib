from collections.abc import Iterable

from django.db import models


def get_model_permission_name(model: models.Model) -> str:
    return f"{model._meta.app_label}__{model._meta.model_name}"  # noqa: SLF001


def get_all_rbac_model_parents(model: models.Model) -> Iterable[models.Model]:
    ...


def has_global_access_to_model(model: models.Model) -> bool:
    ...

