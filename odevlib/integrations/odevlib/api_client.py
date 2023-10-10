"""
This package contains API client that may be used to easily integrate
with other services implemented in ODevLib.

Error handling is seamless when integrating ODevLib services.
"""


from typing import Any

import requests
from requests.exceptions import JSONDecodeError

from odevlib.errors import codes
from odevlib.models.errors import Error


class ODLAPIClient:
    token: str
    base_url: str

    def __init__(self, base_url: str, token: str) -> None:
        self.base_url = base_url
        self.token = token

    def apply_authentication(self, headers: dict, query_params: dict) -> tuple[dict, dict]:
        """
        Allow to customize how authentication is applied to the request.
        Authorization can be either in headers or in query parameters.
        """
        headers.update({"Authorization": f"Token {self.token}"})
        return headers, query_params

    def send_request(
        self,
        method: str,
        url: str,
        body: Any = None,
        query_params: dict | None = None,
        headers: dict[str, Any] | None = None,
    ) -> dict | Error:
        """
        Send a request to external API.

        :param method: HTTP method (GET, POST, PUT, PATCH, DELETE).
        :param url: URL (excluding base URL) to send request to.
        :param body: Body of the request, if any.
        :param query_params: Query parameters to send with request, if any.
        :return: Response from external API.
        """

        if query_params is None:
            query_params = {}
        if headers is None:
            headers = {}
        headers, query_params = self.apply_authentication(headers, query_params)

        response = requests.request(
            method,
            f"{self.base_url}/{url}",
            json=body,
            headers=headers,
            params=query_params,
        )

        try:
            json = response.json()
            # Handle ODevLib errors on the other side
            if "error_code" in json:
                return Error(
                    error_code=json["error_code"],
                    eng_description=json["eng_description"],
                    ui_description=json["ui_description"],
                )
        except JSONDecodeError:
            return Error(
                error_code=codes.unhandled_error,
                eng_description=f"Couldn't parse JSON when sending request to external API. Status code: {response.status_code}.",
                ui_description=f"Couldn't parse JSON when sending request to external API. Status code: {response.status_code}.",
            )

        return json

    def get(
        self,
        url: str,
        query_params: dict | None = None,
    ) -> dict | Error:
        """
        Send GET request to external API.

        :param url: URL (excluding base URL) to send request to.
        :param query_params: Query parameters to send with request, if any.
        :return: Response from external API.
        """

        if query_params is None:
            query_params = {}
        return self.send_request("GET", url, query_params=query_params)

    def post(
        self,
        url: str,
        body: Any,
        query_params: dict | None = None,
    ) -> dict | Error:
        """
        Send POST request to external API.

        :param url: URL (excluding base URL) to send request to.
        :param body: Body of request.
        :param query_params: Query parameters to send with request, if any.
        :return: Response from external API.
        """

        if query_params is None:
            query_params = {}
        return self.send_request("POST", url, body, query_params=query_params)

    def put(
        self,
        url: str,
        body: Any,
        query_params: dict | None = None,
    ) -> dict | Error:
        """
        Send PUT request to external API.

        :param url: URL (excluding base URL) to send request to.
        :param body: Body of request.
        :param query_params: Query parameters to send with request, if any.
        :return: Response from external API.
        """

        if query_params is None:
            query_params = {}
        return self.send_request("PUT", url, body, query_params=query_params)

    def patch(
        self,
        url: str,
        body: Any,
        query_params: dict | None = None,
    ) -> dict | Error:
        """
        Send PATCH request to external API.

        :param url: URL (excluding base URL) to send request to.
        :param body: Body of request.
        :param query_params: Query parameters to send with request, if any.
        :return: Response from external API.
        """

        if query_params is None:
            query_params = {}
        return self.send_request("PATCH", url, body, query_params=query_params)

    def delete(
        self,
        url: str,
        query_params: dict | None = None,
    ) -> dict | Error:
        """
        Send DELETE request to external API.

        :param url: URL (excluding base URL) to send request to.
        :param query_params: Query parameters to send with request, if any.
        :return: Response from external API.
        """

        if query_params is None:
            query_params = {}
        return self.send_request("DELETE", url, query_params=query_params)
