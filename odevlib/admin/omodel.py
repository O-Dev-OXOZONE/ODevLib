from django.contrib import admin
from django.contrib.auth.models import AbstractUser, User
from django.http import HttpRequest
from typing import Any

from odevlib.models.omodel import OModel


class OModelAdmin(admin.ModelAdmin):
    readonly_fields = ["created_by", "updated_by"]

    def save_model(
        self, request: HttpRequest, obj: OModel, form: Any, change: bool
    ) -> None:
        user: User = request.user  # type: ignore
        assert isinstance(user, AbstractUser)
        obj.save(user=user)
