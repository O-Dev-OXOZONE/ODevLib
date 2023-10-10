import threading

from django.contrib.auth.models import AbstractUser
from rest_framework.request import Request
from rest_framework.response import Response

request_local = threading.local()
user_local = None  # type: ignore


def get_request() -> Request | None:
    return getattr(request_local, "request", None)


def get_user() -> AbstractUser | None:
    request = getattr(request_local, "request", None)
    if request is None:
        if user_local is not None:
            return user_local
        return None
    return request.user


class CurrentUserMiddleware:
    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request: Request) -> Response:
        request_local.request = request
        return self.get_response(request)

    def process_exception(self, request: Request, exception) -> None:
        request_local.request = None

    def process_template_response(self, request: Request, response: Response) -> Response:
        request_local.request = None
        return response
