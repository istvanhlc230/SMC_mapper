"""Shared standard-library HTTP GET transport with bounded retry and decoding."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any, Mapping


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
                with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
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
