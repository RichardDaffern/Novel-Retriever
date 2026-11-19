"""Offline tests for bounded NovelFull HTTPS transport; no live downloads."""
import io
from http.client import RemoteDisconnected
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError

from tools import novelfull_http


BOOK = "https://novelfull.com/a-will-eternal.html"


class Response:
    def __init__(self, body, *, status=200, url=BOOK, headers=None):
        self.body = body
        self.status = status
        self.url = url
        self.headers = headers or {}
    def read(self, size):
        return self.body[:size]
    def __enter__(self):
        return self
    def __exit__(self, *_):
        return False


class TransportTests(unittest.TestCase):
    def test_cli_runner_can_be_invoked_from_unrelated_directory(self):
        runner = Path(__file__).resolve().parents[1] / "tools" / "fanficfare_progress_runner.py"
        with tempfile.TemporaryDirectory() as cwd:
            result = subprocess.run(
                [sys.executable, str(runner), "--help"],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=20,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Usage", result.stdout)

    def test_allowlist_blocks_other_hosts_and_http(self):
        self.assertTrue(novelfull_http._allowed(BOOK))
        for url in (
            "http://novelfull.com/a.html", "https://evil.example/a.html",
            "https://novelfull.com.evil.example/a.html",
            "https://user:pass@novelfull.com/a.html",
            "https://novelfull.com:8443/a.html",
        ):
            self.assertFalse(novelfull_http._allowed(url), url)

    def test_readable_response_is_returned_with_identity(self):
        opener = Mock()
        opener.open.return_value = Response(b"<html>Valid story page</html>")
        with patch.object(novelfull_http, "build_opener", return_value=opener):
            data, url = novelfull_http._get_bytes(BOOK, {"User-Agent": "NovelLibrary"}, 8)
        self.assertEqual(data, b"<html>Valid story page</html>")
        self.assertEqual(url, BOOK)
        self.assertEqual(opener.open.call_args.kwargs["timeout"], 8)

    def test_transient_remote_disconnect_gets_only_one_paced_retry(self):
        opener = Mock()
        opener.open.side_effect = [
            RemoteDisconnected("Connection dropped"),
            Response(b"<html>Valid chapter</html>"),
        ]
        with patch.object(novelfull_http, "build_opener", return_value=opener), \
                patch.object(novelfull_http.time, "sleep") as sleeper:
            data, url = novelfull_http._get_bytes(BOOK, {}, 8)
        self.assertEqual((data, url), (b"<html>Valid chapter</html>", BOOK))
        self.assertEqual(opener.open.call_count, 2)
        sleeper.assert_called_once_with(novelfull_http.TRANSIENT_RETRY_DELAY_SECONDS)

    def test_wrapped_transient_timeout_is_retried_once(self):
        opener = Mock()
        opener.open.side_effect = [
            URLError(TimeoutError("Read timed out")),
            Response(b"<html>Valid chapter</html>"),
        ]
        with patch.object(novelfull_http, "build_opener", return_value=opener), \
                patch.object(novelfull_http.time, "sleep") as sleeper:
            data, _ = novelfull_http._get_bytes(BOOK, {}, 8)
        self.assertEqual(data, b"<html>Valid chapter</html>")
        self.assertEqual(opener.open.call_count, 2)
        sleeper.assert_called_once()

    def test_repeated_connection_loss_stops_after_two_attempts(self):
        opener = Mock()
        opener.open.side_effect = RemoteDisconnected("Connection dropped")
        with patch.object(novelfull_http, "build_opener", return_value=opener), \
                patch.object(novelfull_http.time, "sleep") as sleeper:
            with self.assertRaises(RemoteDisconnected):
                novelfull_http._get_bytes(BOOK, {}, 8)
        self.assertEqual(opener.open.call_count, 2)
        sleeper.assert_called_once()

    def test_http_429_and_nontransient_network_errors_never_retry(self):
        from fanficfare.exceptions import HTTPErrorFFF
        for failure, error in (
            (HTTPError(BOOK, 429, "Too Many Requests", {}, None), HTTPErrorFFF),
            (URLError("DNS lookup failed"), URLError),
        ):
            with self.subTest(error=error.__name__):
                opener = Mock()
                opener.open.side_effect = failure
                with patch.object(novelfull_http, "build_opener", return_value=opener), \
                        patch.object(novelfull_http.time, "sleep") as sleeper:
                    with self.assertRaises(error):
                        novelfull_http._get_bytes(BOOK, {}, 8)
                self.assertEqual(opener.open.call_count, 1)
                sleeper.assert_not_called()

    def test_explicit_cloudflare_challenge_fails_closed(self):
        from fanficfare.exceptions import HTTPErrorFFF
        opener = Mock()
        opener.open.side_effect = HTTPError(
            BOOK, 403, "Forbidden", {"cf-mitigated": "challenge"}, io.BytesIO(b"challenge"),
        )
        with patch.object(novelfull_http, "build_opener", return_value=opener):
            with self.assertRaises(HTTPErrorFFF) as exc:
                novelfull_http._get_bytes(BOOK, {}, 8)
        self.assertEqual(exc.exception.status_code, 403)
        self.assertIn("access challenge", str(exc.exception))

    def test_oversized_response_fails_closed(self):
        opener = Mock()
        opener.open.return_value = Response(b"x" * (novelfull_http.MAX_RESPONSE_BYTES + 1))
        with patch.object(novelfull_http, "build_opener", return_value=opener):
            with self.assertRaisesRegex(ValueError, "size limit"):
                novelfull_http._get_bytes(BOOK, {}, 8)

    def test_only_novelfull_get_uses_fallback_and_restores_original(self):
        from fanficfare.fetchers.fetcher_requests import RequestsFetcher
        with patch.object(RequestsFetcher, "request", return_value="untouched") as original:
            with patch.object(novelfull_http, "_get_bytes", return_value=(b"OK", BOOK)) as fetch:
                try:
                    novelfull_http.enable()
                    config = SimpleNamespace(getConfig=lambda key, default=None: default)
                    resp = RequestsFetcher.request(config, "GET", BOOK, headers={"Accept": "text/html"})
                    self.assertEqual(resp.content, b"OK")
                    self.assertEqual(resp.redirecturl, BOOK)
                    self.assertEqual(fetch.call_count, 1)
                    result = RequestsFetcher.request(config, "GET", "https://example.org/story")
                    self.assertEqual(result, "untouched")
                    original.assert_called_once()
                finally:
                    novelfull_http.disable()
            self.assertIs(RequestsFetcher.request, original)


if __name__ == "__main__":
    unittest.main()
