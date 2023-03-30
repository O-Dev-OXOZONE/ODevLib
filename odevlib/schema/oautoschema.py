import typing

import drf_spectacular.openapi
from drf_spectacular.drainage import error
from rest_framework.exceptions import APIException

from odevlib.views import OViewSet


class OAutoSchema(drf_spectacular.openapi.AutoSchema):
    """
    Provides drf_spectacular OpenAPI schema generator for OViewSet.
    """

    def get_summary(self) -> str:
        model_name = self.view.get_queryset().model._meta.verbose_name
        if self._is_list_view(self.view.serializer_class):
            return f"Получить список {model_name}"
        elif self.method == "GET":
            return f"Получить {model_name}"
        elif self.method == "PUT":
            return f"Обновить {model_name}"
        elif self.method == "PATCH":
            return f"Частично обновить {model_name}"
        elif self.method == "POST":
            return f"Создать {model_name}"
        elif self.method == "DELETE":
            return f"Удалить {model_name}"

        return f"Неизвестная операция OViewSet для {self.view.get_queryset().model._meta.verbose_name}"

    def get_description(self):
        return None

    def get_action(self) -> str:
        """
        Returns DRF action for the current view (create, retrieve, list, update, partial_update, destroy).
        """
        if self._is_list_view(self.view.serializer_class):
            return "list"
        elif self.method == "GET":
            return "retrieve"
        elif self.method == "PUT":
            return "update"
        elif self.method == "POST":
            return "create"
        elif self.method == "PATCH":
            return "partial_update"
        elif self.method == "DELETE":
            return "destroy"

        raise APIException(f"Unknown action {self.method}")

    def get_override_parameters(self):
        return self.view.additional_query_parameters.get(self.get_action(), [])

    def get_request_serializer(self) -> typing.Any:
        if not isinstance(self.view, OViewSet):
            error("Trying to use OAutoSchema on non-OViewSet view.")
        if self.method == "POST":
            return self.view.create_serializer_class
        elif self.method in ["PUT", "PATCH"]:
            return self.view.update_serializer_class or self.view.create_serializer_class
        else:
            return None

    def get_response_serializers(self) -> typing.Any:
        if not isinstance(self.view, OViewSet):
            error("Trying to use OAutoSchema on non-OViewSet view.")
        return self.view.serializer_class
