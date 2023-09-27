import logging
import time
from collections.abc import Callable

from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from odevlib.models.logging import RequestLogEntry


class TimescaleLoggingMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        # Short-circuit if loki logger should be disabled as requested by cookies
        if request.COOKIES.get("disable_timescale_logger", "false") == "true":
            return self.get_response(request)

        start_timestamp = time.time()

        response: HttpResponse = self.get_response(request)

        end_timestamp = time.time()

        user = None if isinstance(request.user, AnonymousUser) else request.user

        entry = RequestLogEntry(
            time=timezone.now(),
            user=user,
            method=request.method or "unknown",
            path=request.path,
            code=response.status_code,
            processing_time=int((end_timestamp - start_timestamp) * 1000),
            application="back",
        )

        # If response is not OK, include it in extra as well
        if not str(response.status_code).startswith("2"):
            entry.request = str(request.headers)
            entry.response = response.content.decode("utf-8")

        try:
            entry.save()
        except Exception:
            logging.exception("Error occurred while saving request log entry")
        return response
