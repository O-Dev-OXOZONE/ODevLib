from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
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

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
        *args,
        **kwargs,
    ) -> None:
        user: User = kwargs.get("user", None)
        if user is None and ((_user := get_user()) is not None):
            user = _user
        if user is None:
            raise ValueError(
                "User was not passed to the {self.__class__.__name__} save method and "
                f"could not be retrieved from the middleware"
            )

        self.updated_by = user  # type: ignore
        if self._state.adding is True:
            self.created_by = user  # type: ignore

        super().save(force_insert, force_update, using, update_fields)
