from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models
from simple_history.models import HistoricalRecords  # type: ignore[import]

from odevlib.middleware import get_user

if TYPE_CHECKING:
    from django.contrib.auth.models import User


class OModel(models.Model):
    """
    Base model that keeps track of the creator, updater and create/update date.
    """

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

    class Meta:
        abstract = True

    def save(
        self,
        force_insert=False,  # noqa: ANN001
        force_update=False,  # noqa: ANN001
        using=None,  # noqa: ANN001
        update_fields=None,  # noqa: ANN001
        *args,
        **kwargs,
    ) -> None:
        user: User = kwargs.get("user", None)
        if user is None and ((_user := get_user()) is not None):
            user = _user
        if user is None:
            msg = (
                f"User was not passed to the {self.__class__.__name__} "
                "save method and could not be retrieved from the middleware"
            )
            raise ValueError(msg)

        self.updated_by = user  # type: ignore[assignment]
        if self._state.adding is True:
            self.created_by = user  # type: ignore[assignment]

        self.before_save(*args, **kwargs)

        super().save(force_insert, force_update, using, update_fields)

    def before_save(self, *args, **kwargs) -> None:
        """
        Allow customizing behavior before saving the model.
        """
