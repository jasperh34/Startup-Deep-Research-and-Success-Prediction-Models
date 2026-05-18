from __future__ import annotations

import json
import ssl
from http.client import HTTPResponse
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class HttpRequestError(RuntimeError):
    def __init__(self, message: str, status: int | None = None):
        super().__init__(message)
        self.status = status


def request_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    payload: Any | None = None,
    timeout: float = 20,
) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = Request(
        url,
        data=body,
        method=method,
        headers={"Content-Type": "application/json", **(headers or {})},
    )

    try:
        with _open_url(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        raise HttpRequestError(
            f"Request failed with status {error.code}: {url}"
            f"{f' - {details}' if details else ''}",
            status=error.code,
        ) from error
    except URLError as error:
        raise HttpRequestError(f"Request failed: {error.reason}") from error


def head_url(url: str, *, timeout: float = 2.5) -> tuple[int, str]:
    request = Request(url, method="HEAD")
    try:
        with _open_url(request, timeout=timeout) as response:
            return response.status, response.url
    except HTTPError as error:
        return error.code, error.url
    except URLError as error:
        raise HttpRequestError(f"HEAD failed: {error.reason}") from error


def _open_url(request: Request, *, timeout: float) -> HTTPResponse:
    try:
        return urlopen(request, timeout=timeout)
    except URLError as error:
        if isinstance(error.reason, ssl.SSLCertVerificationError):
            context = ssl._create_unverified_context()
            return urlopen(request, timeout=timeout, context=context)
        raise
