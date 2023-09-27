from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from odevlib.models.logging import RequestLogEntry


def request_logs_view(request: HttpRequest) -> HttpResponse:
    if not request.user.is_superuser:
        # TODO: replace this with a 403 page built into ODevLib? Not all project will have this template.
        return render(request, "403.html")

    logs = RequestLogEntry.timescale.order_by("-time").select_related("user")[:10000]

    return render(
        request,
        "admin/request_logs.html",
        context={
            "logs": logs,
        },
    )
