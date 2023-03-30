import threading
from typing import Union

from django.contrib.auth.models import AbstractUser
from rest_framework.request import Request

request_local = threading.local()


def get_request() -> Union[Request, None]:
    return getattr(request_local, 'request', None)


def get_user() -> Union[AbstractUser, None]:
    request = getattr(request_local, 'request', None)
    if request is None:
        return None
    return request.user


class CurrentUserMiddleware():
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_local.request = request
        return self.get_response(request)

    def process_exception(self, request, exception):
        request_local.request = None

    def process_template_response(self, request, response):
        request_local.request = None
        return response
