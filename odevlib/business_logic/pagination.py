from typing import TypeVar

from django.db import models
from django.db.models.query import QuerySet

from odevlib.errors import codes
from odevlib.models.errors import Error

M = TypeVar("M", bound=models.Model)


def paginate_queryset(
    qs: QuerySet[M],
    first_id: str | None,
    last_id: str | None,
    count: int | str | None,
) -> tuple[QuerySet[M], int, int] | Error:
    if isinstance(count, str):
        try:
            count = int(count)
        except ValueError:
            return Error(
                error_code=codes.invalid_request_data,
                eng_description="count must be int",
                ui_description="count must be int",
            )

    if first_id is not None and last_id is not None:
        return Error(
            error_code=codes.invalid_request_data,
            eng_description="Can't use both first_id and last_id. Please specify only one argument.",
            ui_description="Can't use both first_id and last_id. Please specify only one argument.",
        )

    try:
        first_id_num = int(first_id) if first_id is not None else None
    except ValueError:
        return Error(
            error_code=codes.invalid_request_data,
            eng_description="first_id must be int",
            ui_description="first_id must be int",
        )

    try:
        last_id_num = int(last_id) if last_id is not None else None
    except ValueError:
        return Error(
            error_code=codes.invalid_request_data,
            eng_description="last_id must be int",
            ui_description="last_id must be int",
        )

    queryset = qs

    if first_id_num is not None:
        queryset = queryset.filter(pk__lt=first_id_num)
        available_count = queryset.count()
        queryset = queryset[:count]
        filtered_count = queryset.count()
    elif last_id_num is not None:
        queryset = queryset.filter(pk__gt=last_id_num)
        available_count = queryset.count()
        queryset = queryset[:count]
        filtered_count = queryset.count()
    else:
        available_count = queryset.count()
        queryset = queryset[:count]
        filtered_count = queryset.count()

    return queryset, available_count, filtered_count
