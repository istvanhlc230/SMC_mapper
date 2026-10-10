"""Shared standard-library HTTP GET transport with bounded retry and decoding."""
from __future__ import annotations

import http.client
import json
import socket
import time
import urllib.error
import urllib.request
from typing import Any, Mapping


def _ipv4_first_create_connection(
    address: tuple[str, int],
    timeout: float | object = socket._GLOBAL_DEFAULT_TIMEOUT,
    source_address: tuple[str, int] | None = None,
    *,
    all_errors: bool = False,
) -> socket.socket:
    """Create a TCP connection by trying IPv4 addresses before IPv6 addresses."""
    host, port = address
    address_infos = socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM)
    # Preserve DNS order within each family, but avoid waiting on a broken
    # IPv6 route when a working IPv4 route is available.
    address_infos.sort(key=lambda address_info: 0 if address_info[0] == socket.AF_INET else 1)

    connection_errors: list[OSError] = []
    for address_family, socket_type, protocol, _canonical_name, socket_address in address_infos:
        connection_socket = socket.socket(address_family, socket_type, protocol)
        try:
            if timeout is not socket._GLOBAL_DEFAULT_TIMEOUT:
                connection_socket.settimeout(timeout)
            if source_address is not None:
                connection_socket.bind(source_address)
            connection_socket.connect(socket_address)
            return connection_socket
        except OSError as exc:
            connection_errors.append(exc)
            connection_socket.close()

    if not connection_errors:
        raise OSError(f"DNS returned no usable addresses for {host!r}")
    if all_errors and len(connection_errors) > 1:
        raise ExceptionGroup("All resolved addresses failed to connect", connection_errors)
    raise connection_errors[-1]


class _IPv4FirstHTTPConnection(http.client.HTTPConnection):
    """HTTP connection that prefers IPv4 while retaining IPv6 fallback."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._create_connection = _ipv4_first_create_connection


class _IPv4FirstHTTPSConnection(http.client.HTTPSConnection):
    """HTTPS connection that prefers IPv4 while retaining TLS hostname checks."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._create_connection = _ipv4_first_create_connection


class _IPv4FirstHTTPHandler(urllib.request.HTTPHandler):
    """urllib HTTP handler backed by the IPv4-first connection."""

    def http_open(self, request: urllib.request.Request):
        return self.do_open(_IPv4FirstHTTPConnection, request)


class _IPv4FirstHTTPSHandler(urllib.request.HTTPSHandler):
    """urllib HTTPS handler backed by the IPv4-first TLS connection."""

    def https_open(self, request: urllib.request.Request):
        return self.do_open(
            _IPv4FirstHTTPSConnection,
            request,
            context=self._context,
        )


def open_url(
    request: str | urllib.request.Request,
    *,
    timeout_seconds: float = 15.0,
    ipv4_first: bool = False,
):
    """Open an HTTP URL, optionally preferring IPv4 and then falling back to IPv6."""
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    if ipv4_first:
        # build_opener retains the default environment proxy handling and installs
        # our family-ordering transport only for HTTP/HTTPS connections.
        opener = urllib.request.build_opener(
            _IPv4FirstHTTPHandler,
            _IPv4FirstHTTPSHandler,
        )
        return opener.open(request, timeout=timeout_seconds)
    return urllib.request.urlopen(request, timeout=timeout_seconds)


class HttpRequestError(RuntimeError):
    """Raised when an HTTP GET or its requested response decoding fails."""


class HttpClient:
    """Provider-neutral urllib-based HTTP GET helper."""

    @staticmethod
    def get(
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout_seconds: float = 15.0,
        response_format: str = "text",
        retries: int = 1,
        retry_delay_seconds: float = 0.0,
        ipv4_first: bool = False,
    ) -> Any:
        """Fetch bytes, UTF-8 text, or JSON with finite caller-configured retry."""
        if response_format not in {"bytes", "text", "json"}:
            raise ValueError("response_format must be 'bytes', 'text', or 'json'")
        if retries < 1:
            raise ValueError("retries must be at least one")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if retry_delay_seconds < 0:
            raise ValueError("retry_delay_seconds must not be negative")

        last_error: Exception | None = None
        last_message = "HTTP request failed"

        for attempt in range(1, retries + 1):
            try:
                request = urllib.request.Request(url, headers=dict(headers or {}))
                with open_url(
                    request,
                    timeout_seconds=timeout_seconds,
                    ipv4_first=ipv4_first,
                ) as response:
                    response_status = getattr(response, "status", 200)
                    if response_status != 200:
                        raise _HttpStatusError(response_status)
                    payload = response.read()

                if response_format == "bytes":
                    return payload
                decoded_text = payload.decode("utf-8")
                if response_format == "text":
                    return decoded_text
                return json.loads(decoded_text)
            except urllib.error.HTTPError as exc:
                last_error = exc
                last_message = f"HTTP {exc.code}"
            except _HttpStatusError as exc:
                last_error = exc
                last_message = f"HTTP {exc.status_code}"
            except urllib.error.URLError as exc:
                last_error = exc
                last_message = "HTTP network request failed"
            except TimeoutError as exc:
                last_error = exc
                last_message = "HTTP request timed out"
            except UnicodeDecodeError as exc:
                last_error = exc
                last_message = "HTTP response is not valid UTF-8"
            except json.JSONDecodeError as exc:
                last_error = exc
                last_message = "HTTP response is not valid JSON"
            except OSError as exc:
                last_error = exc
                last_message = "HTTP transport failed"

            if attempt < retries and retry_delay_seconds:
                time.sleep(retry_delay_seconds * attempt)

        raise HttpRequestError(last_message) from None


class _HttpStatusError(RuntimeError):
    """Internal representation for a non-success response status."""

    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        super().__init__(f"HTTP {status_code}")
