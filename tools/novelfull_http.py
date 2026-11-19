"""Restricted stdlib HTTP transport for NovelFull's FanFicFare adapter.

Use ordinary Python HTTPS requests with clear identification, bounded content,
a small inter-request interval, and fail-fast handling of access challenges.
The transport is limited to GET requests for novelfull.com. It does not solve
CAPTCHAs, use proxies, fake session cookies, or retry blocked requests.
"""
from __future__ import annotations

import time
from http.client import IncompleteRead, RemoteDisconnected
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import (
    HTTPRedirectHandler,
    Request,
    build_opener,
)

MIN_INTERVAL_SECONDS = 1.5
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
# Retry one interrupted connection, never an HTTP denial or invalid content.
TRANSIENT_RETRY_DELAY_SECONDS = 4
MAX_TRANSIENT_ATTEMPTS = 2
TRANSIENT_ERRORS = (RemoteDisconnected, ConnectionResetError, TimeoutError, IncompleteRead)
_ORIGINAL_REQUEST = None


def _allowed(url: str) -> bool:
    parts = urlsplit(url)
    return (
        parts.scheme == "https"
        and parts.hostname == "novelfull.com"
        and parts.username is None
        and parts.password is None
        and parts.port in (None, 443)
    )


class _DomainRedirects(HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        if not _allowed(newurl):
            return None
        return super().redirect_request(request, fp, code, msg, headers, newurl)


def _get_bytes(url: str, headers: dict, timeout: float) -> tuple[bytes, str]:
    from fanficfare.exceptions import HTTPErrorFFF

    request_headers = {
        str(k): str(v) for k, v in (headers or {}).items()
        if v is not None
    }
    request_headers.setdefault("Accept", "text/html")
    request = Request(url, headers=request_headers, method="GET")
    opener = build_opener(_DomainRedirects())
    for attempt in range(MAX_TRANSIENT_ATTEMPTS):
        try:
            with opener.open(request, timeout=timeout) as response:
                if not _allowed(response.url):
                    raise ValueError("NovelFull redirect left the approved HTTPS host")
                if response.headers.get("cf-mitigated") == "challenge":
                    raise HTTPErrorFFF(url, 403, "Site requested an access challenge")
                content = response.read(MAX_RESPONSE_BYTES + 1)
                if len(content) > MAX_RESPONSE_BYTES:
                    raise ValueError("NovelFull HTTP response exceeded size limit")
                return content, response.url
        except HTTPError as exc:
            # HTTP errors, including 403/429, are never retried.
            message = (
                "Site requested an access challenge"
                if exc.headers.get("cf-mitigated") == "challenge"
                else f"HTTP {exc.code}: {exc.reason}"
            )
            raise HTTPErrorFFF(url, exc.code, message) from exc
        except TRANSIENT_ERRORS:
            if attempt + 1 == MAX_TRANSIENT_ATTEMPTS:
                raise
        except URLError as exc:
            # urllib can wrap a socket timeout/reset in URLError.
            if (not isinstance(exc.reason, TRANSIENT_ERRORS)
                    or attempt + 1 == MAX_TRANSIENT_ATTEMPTS):
                raise
        time.sleep(TRANSIENT_RETRY_DELAY_SECONDS)
    raise AssertionError("Unreachable: attempts exhausted")


def enable() -> None:
    """Patch only NovelFull GET fetches in this CLI process."""
    global _ORIGINAL_REQUEST
    if _ORIGINAL_REQUEST is not None:
        return
    from fanficfare.fetchers.fetcher_requests import RequestsFetcher
    from fanficfare.fetchers.base_fetcher import FetcherResponse

    original = RequestsFetcher.request

    def request(self, method, url, headers=None, parameters=None, json=None):
        if (method != "GET" or not _allowed(url)
                or parameters is not None or json is not None):
            return original(self, method, url, headers, parameters, json)
        last = getattr(self, "_novelfull_last_fetch", None)
        if last is not None:
            time.sleep(max(0.0, MIN_INTERVAL_SECONDS - (time.monotonic() - last)))
        self._novelfull_last_fetch = time.monotonic()
        timeout = float(self.getConfig("connect_timeout", 60))
        content, redirected = _get_bytes(url, headers or {}, timeout)
        return FetcherResponse(content, redirected, False)

    RequestsFetcher.request = request
    _ORIGINAL_REQUEST = original


def disable() -> None:
    """Restore the upstream fetcher after FanFicFare exits."""
    global _ORIGINAL_REQUEST
    if _ORIGINAL_REQUEST is None:
        return
    from fanficfare.fetchers.fetcher_requests import RequestsFetcher
    RequestsFetcher.request = _ORIGINAL_REQUEST
    _ORIGINAL_REQUEST = None
