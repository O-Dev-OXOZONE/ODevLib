from django.conf import settings
from django.db import models
from timescale.db.models.models import TimescaleModel


class RequestLogEntry(TimescaleModel):
    class Meta:
        verbose_name = "Запись лога запросов"
        verbose_name_plural = "Записи лога запросов"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователь",
        on_delete=models.PROTECT,
        related_name="requestlogentries",
        null=True,
        blank=True,
    )
    application = models.TextField(verbose_name="Application name")
    method = models.TextField(verbose_name="HTTP method")
    path = models.TextField(verbose_name="HTTP path")
    code = models.IntegerField(verbose_name="HTTP status code")
    processing_time = models.IntegerField(verbose_name="Request execution time (ms)")
    request = models.TextField(verbose_name="Request body (in case of non-2xx status code)", blank=True, null=True)
    response = models.TextField(verbose_name="Response body (in case of non-2xx status code)", blank=True, null=True)
