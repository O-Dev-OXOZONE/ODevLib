from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords
from o_gpt.users.models import User  # type: ignore

from odevlib.middleware import get_user


class OModel(models.Model):
    """
    Base model that keeps track of the creator, updater and create/update date.
    """

    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="created_%(model_name)ss",
        verbose_name="Создатель",
        on_delete=models.PROTECT,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата редактирования",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="updated_%(model_name)ss",
        verbose_name="Последний редактор",
        on_delete=models.PROTECT,
    )

    history = HistoricalRecords(inherit=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs) -> None:
        user: User = kwargs.get("user", None)
        assert isinstance(user, User)
        if user is None and ((_user := get_user()) is not None):
            user = _user
        if user is None:
            raise ValueError("user was not passed to the OModel")

        self.updated_by = user
        if not self.pk:
            self.created_by = user

        super().save(force_insert, force_update, using, update_fields)
