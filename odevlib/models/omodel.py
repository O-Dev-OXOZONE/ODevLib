from django.db import models
from django.contrib.auth.models import User
from simple_history.models import HistoricalRecords  # type: ignore

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
        User,
        related_name="created_%(model_name)ss",
        verbose_name="Создатель",
        on_delete=models.PROTECT,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата редактирования",
    )
    updated_by = models.ForeignKey(
        User,
        related_name="updated_%(model_name)ss",
        verbose_name="Последний редактор",
        on_delete=models.PROTECT,
    )

    history = HistoricalRecords(inherit=True)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs) -> None:
        user: User = kwargs.get('user', None)
        if user is None and ((_user := get_user()) is not None):
            user = User.objects.get(user=_user)
        if user is None:
            raise ValueError("user was not passed to the OModel")

        self.updated_by = user
        if not self.pk:
            self.created_by = user

        super().save(force_insert, force_update, using, update_fields)
