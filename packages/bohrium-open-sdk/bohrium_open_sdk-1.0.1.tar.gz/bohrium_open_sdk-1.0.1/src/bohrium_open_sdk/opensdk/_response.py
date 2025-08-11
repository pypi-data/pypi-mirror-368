import logging
from typing import Any, Dict, Mapping, Optional
from xml.dom import NotFoundErr

from httpx import Response

from . import _exceptions
from ._exceptions import APIStatusError

logger = logging.getLogger(__name__)


class APIErrorResponse:
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code

    def to_dict(self) -> Dict[str, Any]:
        return {"error": self.message, "status_code": self.status_code}

    def __repr__(self) -> str:
        return f"<APIErrorResponse(status_code={self.status_code}, message='{self.message}')>"


class APIResponse:
    def __init__(self, response: Response, request: Any = None):
        self._response = response
        self._request = request
        self.status_code = response.status_code
        self.headers = response.headers
        self.raise_for_status()
        self._json = self._parse_json(response)
        self._data = self._fetch_data(response)

    def _parse_json(self, response: Response) -> Optional[Any]:
        """Parses the JSON content of the response."""
        try:
            return response.json()
        except ValueError:
            return APIErrorResponse("Invalid JSON response", response.status_code)

    def _fetch_data(self, response: Response) -> Optional[Any]:
        try:
            return response.json().get("data")
        except ValueError:
            return APIErrorResponse("Invalid JSON response", response.status_code)

    @property
    def data(self) -> Optional[Any]:
        try:
            return DotDict(self._json["data"])
        except KeyError:
            raise NotFoundErr("No data found in response")

    @property
    def json(self) -> Optional[Any]:
        return self._json

    def is_success(self) -> bool:
        """Returns True if the response status code indicates success."""
        return 200 <= self.status_code < 300

    def raise_for_status(self):
        """Raises an HTTPError if the response status code indicates an error."""
        if not self.is_success():
            err_msg = f"HTTP Error {self.status_code} for url {self._response.url}, response: {self._response.text}"
            logging.error(err_msg)
            err = self._make_status_error(
                err_msg,
                body=None,
                response=self._response,
            )
            raise err

    def __repr__(self) -> str:
        return (
            f"<APIResponse(status_code={self.status_code}, "
            f"headers={dict(self.headers)}, "
            f"json={self._json})>"
        )

    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: Response,
    ) -> APIStatusError:
        data = body.get("error", body) if isinstance(body, Mapping) else body
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=data)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(
                err_msg, response=response, body=data
            )

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(
                err_msg, response=response, body=data
            )

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=data)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=data)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(
                err_msg, response=response, body=data
            )

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=data)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(
                err_msg, response=response, body=data
            )
        return APIStatusError(err_msg, response=response, body=data)


class DotDict(dict):
    """A dictionary that supports dot notation for accessing values."""

    def __getattr__(self, attr):
        try:
            value = self[attr]
            if isinstance(value, dict):
                return DotDict(value)
            return value
        except KeyError:
            raise AttributeError(f"No such attribute: {attr}")

    def __setattr__(self, attr, value):
        self[attr] = value

    def __delattr__(self, attr):
        try:
            del self[attr]
        except KeyError:
            raise AttributeError(f"No such attribute: {attr}")
