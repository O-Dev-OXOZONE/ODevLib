from typing import Any, Generic, TypeVar

from django.contrib import admin
from django.http import HttpRequest
from typing_extensions import override

from odevlib.models.omodel import OModel

T = TypeVar("T", bound=OModel)


class OModelAdmin(admin.ModelAdmin, Generic[T]):
    readonly_fields: tuple[str, ...] = ("created_by", "updated_by", "created_at", "updated_at")

    @override
    def save_model(self, request: HttpRequest, obj: T, _form: Any, _change: bool) -> None:
        user = request.user
        obj.save(user=user)
