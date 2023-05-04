from django.contrib import admin
from django.contrib.auth.models import User, AbstractUser

from odevlib.models.omodel import OModel


class OModelAdmin(admin.ModelAdmin):
    readonly_fields = ["created_by", "updated_by"]

    def save_model(self, request, obj: OModel, form, change) -> None:
        user: User = request.user
        assert isinstance(user, AbstractUser)
        obj.save(user=user)
