import pathlib
import socket
import sys
import unittest
import urllib.error
from unittest import mock

SCRIPT_DIR = pathlib.Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
import safe_fetch


class FakeResponse:
    def __init__(self, status=200, body=b"<html>ok</html>", headers=None):
        self.status = status
        self.body = body
        self.headers = headers or {"Content-Type": "text/html; charset=utf-8"}

    def getcode(self):
        return self.status

    def info(self):
        return self.headers

    def read(self, amount=-1):
        if amount < 0:
            result, self.body = self.body, b""
            return result
        result, self.body = self.body[:amount], self.body[amount:]
        return result


class FakeOpener:
    def __init__(self, responses):
        self.responses = iter(responses)

    def open(self, request, timeout):
        response = next(self.responses)
        if isinstance(response, BaseException):
            raise response
        return response


PUBLIC_DNS = [
    (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0)),
]


class SafeFetchTests(unittest.TestCase):
    def test_http_and_https_urls_are_accepted(self):
        self.assertEqual(safe_fetch.normalize_url("http://example.com"), "http://example.com/")
        self.assertEqual(safe_fetch.normalize_url("https://example.com/path"), "https://example.com/path")

    def test_unsupported_schemes_and_credentials_are_rejected(self):
        for url in (
            "ftp://example.com/file",
            "file:///tmp/site",
            "javascript:alert(1)",
            "https://user@example.com",
            "https://[2001:db8::1",
        ):
            with self.assertRaises(safe_fetch.FetchValidationError):
                safe_fetch.normalize_url(url)

    def test_local_hostnames_and_private_ip_literals_are_rejected(self):
        for url in (
            "http://localhost",
            "http://127.0.0.1",
            "http://10.0.0.1",
            "http://172.16.0.1",
            "http://192.168.1.1",
            "http://169.254.1.1",
            "http://[::1]",
            "http://[fc00::1]",
            "http://[fe80::1]",
        ):
            with self.assertRaises(safe_fetch.FetchValidationError):
                safe_fetch.normalize_url(url)

    @mock.patch.object(safe_fetch.socket, "getaddrinfo", return_value=PUBLIC_DNS)
    @mock.patch.object(safe_fetch.urllib.request, "build_opener")
    def test_safe_hostname_and_address_are_accepted(self, build_opener, _getaddrinfo):
        build_opener.return_value = FakeOpener([FakeResponse()])
        result = safe_fetch.safe_fetch("https://example.com")
        self.assertIsNone(result["error"])
        self.assertEqual(result["status"], 200)

    @mock.patch.object(
        safe_fetch.socket,
        "getaddrinfo",
        return_value=[(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.4", 0))],
    )
    @mock.patch.object(safe_fetch.urllib.request, "build_opener")
    def test_hostname_resolving_to_private_address_is_rejected(self, build_opener, _getaddrinfo):
        build_opener.return_value = FakeOpener([FakeResponse()])
        result = safe_fetch.safe_fetch("https://public.example")
        self.assertEqual(result["error_code"], "fetch_blocked")

    @mock.patch.object(
        safe_fetch.socket,
        "getaddrinfo",
        return_value=[
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.168.1.10", 0)),
        ],
    )
    @mock.patch.object(safe_fetch.urllib.request, "build_opener")
    def test_any_blocked_resolved_address_rejects_hostname(self, build_opener, _getaddrinfo):
        build_opener.return_value = FakeOpener([FakeResponse()])
        result = safe_fetch.safe_fetch("https://multi-address.example")
        self.assertEqual(result["error_code"], "fetch_blocked")

    @mock.patch.object(safe_fetch.socket, "getaddrinfo", return_value=PUBLIC_DNS)
    @mock.patch.object(safe_fetch.urllib.request, "build_opener")
    def test_redirect_to_private_address_is_rejected(self, build_opener, _getaddrinfo):
        build_opener.return_value = FakeOpener(
            [
                FakeResponse(302, b"", {"Location": "http://127.0.0.1/admin"}),
            ]
        )
        result = safe_fetch.safe_fetch("https://example.com")
        self.assertEqual(result["error_code"], "fetch_blocked")

    @mock.patch.object(safe_fetch.socket, "getaddrinfo", return_value=PUBLIC_DNS)
    @mock.patch.object(safe_fetch.urllib.request, "build_opener")
    def test_redirect_limit_is_enforced(self, build_opener, _getaddrinfo):
        build_opener.return_value = FakeOpener(
            [
                FakeResponse(302, b"", {"Location": "https://example.com/one"}),
                FakeResponse(302, b"", {"Location": "https://example.com/two"}),
            ]
        )
        result = safe_fetch.safe_fetch("https://example.com", max_redirects=1)
        self.assertEqual(result["error_code"], "redirect_limit")

    @mock.patch.object(safe_fetch.socket, "getaddrinfo", return_value=PUBLIC_DNS)
    @mock.patch.object(safe_fetch.urllib.request, "build_opener")
    def test_oversized_response_is_rejected(self, build_opener, _getaddrinfo):
        build_opener.return_value = FakeOpener([FakeResponse(body=b"0123456789")])
        result = safe_fetch.safe_fetch("https://example.com", max_bytes=5)
        self.assertEqual(result["error_code"], "response_too_large")

    @mock.patch.object(safe_fetch.socket, "getaddrinfo", return_value=PUBLIC_DNS)
    @mock.patch.object(safe_fetch.urllib.request, "build_opener")
    def test_timeout_is_controlled(self, build_opener, _getaddrinfo):
        build_opener.return_value = FakeOpener([TimeoutError()])
        result = safe_fetch.safe_fetch("https://example.com")
        self.assertEqual(result["error_code"], "network_error")

    @mock.patch.object(safe_fetch.socket, "getaddrinfo", return_value=PUBLIC_DNS)
    @mock.patch.object(safe_fetch.urllib.request, "build_opener")
    def test_http_error_preserves_status_and_headers(self, build_opener, _getaddrinfo):
        build_opener.return_value = FakeOpener(
            [
                urllib.error.HTTPError(
                    "https://example.com/robots.txt",
                    404,
                    "Not Found",
                    {"Content-Type": "text/plain"},  # type: ignore[arg-type]
                    None,
                )
            ]
        )
        result = safe_fetch.safe_fetch("https://example.com/robots.txt")
        self.assertEqual(result["error_code"], "http_status")
        self.assertEqual(result["status"], 404)
        self.assertEqual(result["headers"]["Content-Type"], "text/plain")

    @mock.patch.object(safe_fetch.socket, "getaddrinfo", return_value=PUBLIC_DNS)
    @mock.patch.object(safe_fetch.urllib.request, "build_opener")
    def test_html_content_type_is_case_insensitive(self, build_opener, _getaddrinfo):
        header_names = (
            "Content-Type",
            "content-type",
            "CONTENT-TYPE",
            "CoNtEnT-TyPe",
        )
        content_types = (
            "text/html",
            "text/html; charset=utf-8",
            "application/xhtml+xml",
        )
        for header_name in header_names:
            for content_type in content_types:
                with self.subTest(header_name=header_name, content_type=content_type):
                    build_opener.return_value = FakeOpener([FakeResponse(headers={header_name: content_type})])
                    result = safe_fetch.safe_fetch("https://example.com", require_html=True)
                    self.assertIsNone(result["error"])
                    self.assertEqual(result["status"], 200)

    @mock.patch.object(safe_fetch.socket, "getaddrinfo", return_value=PUBLIC_DNS)
    @mock.patch.object(safe_fetch.urllib.request, "build_opener")
    def test_non_html_content_is_not_parsed(self, build_opener, _getaddrinfo):
        build_opener.return_value = FakeOpener([FakeResponse(headers={"Content-Type": "application/pdf"})])
        result = safe_fetch.safe_fetch("https://example.com", require_html=True)
        self.assertEqual(result["error_code"], "content_type")
        self.assertEqual(result["html"], "")

    @mock.patch.object(safe_fetch.socket, "getaddrinfo", side_effect=socket.gaierror)
    @mock.patch.object(safe_fetch.urllib.request, "build_opener")
    def test_dns_failure_is_controlled(self, build_opener, _getaddrinfo):
        build_opener.return_value = FakeOpener([FakeResponse()])
        result = safe_fetch.safe_fetch("https://unresolvable.example")
        self.assertEqual(result["error_code"], "fetch_blocked")

    @mock.patch.object(safe_fetch.urllib.request, "build_opener")
    def test_malformed_url_returns_controlled_failure(self, build_opener):
        build_opener.return_value = FakeOpener([FakeResponse()])
        result = safe_fetch.safe_fetch("https://[2001:db8::1")
        self.assertEqual(result["error_code"], "fetch_blocked")


if __name__ == "__main__":
    unittest.main()
