"""Bounded, SSRF-aware HTTP fetching for the audit engine."""

import ipaddress
import socket
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_TIMEOUT_SECONDS = 10
DEFAULT_MAX_REDIRECTS = 3
DEFAULT_MAX_RESPONSE_BYTES = 2 * 1024 * 1024
DEFAULT_MAX_ROBOTS_BYTES = 256 * 1024

_LOCAL_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
    "ip6-localhost",
    "ip6-loopback",
    "local",
    "broadcasthost",
    "0.0.0.0",
}
_LOCAL_SUFFIXES = (
    ".local",
    ".internal",
    ".lan",
    ".home.arpa",
    ".localhost",
    ".test",
    ".example",
    ".invalid",
)
_REDIRECT_STATUSES = {301, 302, 303, 307, 308}


class FetchValidationError(ValueError):
    """Raised when a URL or resolved destination is unsafe."""


def normalize_url(url):
    """Normalize a user URL and reject unsupported or ambiguous destinations."""
    if not isinstance(url, str) or not url.strip():
        raise FetchValidationError("empty URL")
    candidate = url.strip()
    if "://" not in candidate:
        candidate = "https://" + candidate
    try:
        parsed = urllib.parse.urlsplit(candidate)
    except ValueError as exc:
        raise FetchValidationError("malformed URL") from exc
    if parsed.scheme.lower() not in {"http", "https"}:
        raise FetchValidationError("unsupported URL scheme")
    if parsed.username is not None or parsed.password is not None:
        raise FetchValidationError("URL credentials are not allowed")
    if not parsed.hostname:
        raise FetchValidationError("URL hostname is required")
    hostname = parsed.hostname.rstrip(".").lower()
    if hostname in _LOCAL_HOSTNAMES or hostname.endswith(_LOCAL_SUFFIXES):
        raise FetchValidationError("local hostname is not allowed")

    # Reject integer/numeric representations of IPs (e.g. 2130706433 -> 127.0.0.1)
    if hostname.isdigit():
        try:
            num = int(hostname)
            literal_num_ip = ipaddress.ip_address(num)
            if (
                not literal_num_ip.is_global
                or literal_num_ip.is_loopback
                or literal_num_ip.is_private
                or literal_num_ip.is_link_local
            ):
                raise FetchValidationError("non-public IP address is not allowed")
        except (ValueError, OverflowError):
            raise FetchValidationError("malformed numeric IP hostname")

    try:
        literal_ip = ipaddress.ip_address(hostname)
    except ValueError:
        literal_ip = None
    if literal_ip is not None:
        if isinstance(literal_ip, ipaddress.IPv6Address) and literal_ip.ipv4_mapped:
            mapped = literal_ip.ipv4_mapped
            if not mapped.is_global or mapped.is_loopback or mapped.is_private or mapped.is_link_local:
                raise FetchValidationError("non-public IP address is not allowed")
        if (
            not literal_ip.is_global
            or literal_ip.is_loopback
            or literal_ip.is_private
            or literal_ip.is_link_local
            or literal_ip.is_multicast
            or literal_ip.is_reserved
            or literal_ip.is_unspecified
        ):
            raise FetchValidationError("non-public IP address is not allowed")
    try:
        port = parsed.port
    except ValueError as exc:
        raise FetchValidationError("invalid URL port") from exc
    if port is not None and port not in {80, 443}:
        raise FetchValidationError("non-web port is not allowed")
    netloc = hostname
    if ":" in hostname and not hostname.startswith("["):
        netloc = f"[{hostname}]"
    if port is not None:
        netloc = f"{netloc}:{port}"
    return urllib.parse.urlunsplit((parsed.scheme.lower(), netloc, parsed.path or "/", parsed.query, ""))


def _validate_resolved_addresses(hostname, port):
    try:
        addresses = socket.getaddrinfo(
            hostname,
            port,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as exc:
        raise FetchValidationError("hostname resolution failed") from exc
    if not addresses:
        raise FetchValidationError("hostname resolved to no addresses")
    for address in addresses:
        ip_text = address[4][0]
        try:
            ip = ipaddress.ip_address(ip_text)
        except ValueError as exc:
            raise FetchValidationError("hostname resolved to an invalid address") from exc
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
            mapped = ip.ipv4_mapped
            if not mapped.is_global or mapped.is_loopback or mapped.is_private or mapped.is_link_local:
                raise FetchValidationError("hostname resolved to a non-public address")
        if (
            not ip.is_global
            or ip.is_loopback
            or ip.is_private
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            raise FetchValidationError("hostname resolved to a non-public address")


def _read_bounded(response, max_bytes):
    body = bytearray()
    while len(body) < max_bytes:
        chunk = response.read(min(64 * 1024, max_bytes - len(body)))
        if not chunk:
            return bytes(body)
        body.extend(chunk)
    if response.read(1):
        raise FetchValidationError("response exceeded maximum size")
    return bytes(body)


def safe_fetch(
    url,
    *,
    timeout=DEFAULT_TIMEOUT_SECONDS,
    max_redirects=DEFAULT_MAX_REDIRECTS,
    max_bytes=DEFAULT_MAX_RESPONSE_BYTES,
    require_html=False,
):
    """Fetch a public HTTP(S) resource with DNS, redirect, and size controls."""
    try:
        current_url = normalize_url(url)
    except FetchValidationError as exc:
        return _failure("fetch_blocked", str(exc))
    opener = urllib.request.build_opener(_NoRedirectHandler())

    for redirect_count in range(max_redirects + 1):
        parsed = urllib.parse.urlsplit(current_url)
        try:
            _validate_resolved_addresses(
                parsed.hostname,
                parsed.port or (443 if parsed.scheme == "https" else 80),
            )
            request = urllib.request.Request(
                current_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; BrandAIAuditBot/1.0; +https://agentskills.io)",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                },
            )
            response = opener.open(request, timeout=timeout)
        except urllib.error.HTTPError as exc:
            if exc.code in _REDIRECT_STATUSES:
                response = exc
            else:
                return _failure(
                    "http_status",
                    f"HTTP status {exc.code}",
                    exc.code,
                    dict(exc.headers or {}),
                )
        except (urllib.error.URLError, TimeoutError):
            return _failure("network_error", "network request failed or timed out")
        except FetchValidationError as exc:
            return _failure("fetch_blocked", str(exc))

        status = response.getcode() or 0
        if status in _REDIRECT_STATUSES:
            if redirect_count >= max_redirects:
                return _failure("redirect_limit", "redirect limit exceeded")
            location = response.headers.get("Location")
            if not location:
                return _failure("redirect_error", "redirect response missing Location")
            try:
                current_url = normalize_url(urllib.parse.urljoin(current_url, location))
            except FetchValidationError as exc:
                return _failure("fetch_blocked", str(exc))
            continue

        headers = dict(response.info())
        content_type_header = next(
            (value for key, value in headers.items() if key.lower() == "content-type"),
            "",
        )
        content_type = content_type_header.split(";", 1)[0].strip().lower()
        if require_html and content_type not in {"text/html", "application/xhtml+xml"}:
            return _failure("content_type", "response is not an HTML document", status, headers)
        try:
            body = _read_bounded(response, max_bytes)
        except FetchValidationError as exc:
            return _failure("response_too_large", str(exc), status, headers)
        return {
            "status": status,
            "headers": headers,
            "body": body,
            "html": body.decode("utf-8", errors="replace"),
            "url": current_url,
            "error": None,
            "error_code": None,
        }
    return _failure("redirect_limit", "redirect limit exceeded")


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

    def http_error_301(self, req, fp, code, msg, headers):
        raise urllib.error.HTTPError(req.full_url, code, msg, headers, fp)

    http_error_302 = http_error_301
    http_error_303 = http_error_301
    http_error_307 = http_error_301
    http_error_308 = http_error_301


def _failure(code, message, status=0, headers=None):
    return {
        "status": status,
        "headers": headers or {},
        "body": b"",
        "html": "",
        "url": None,
        "error": message,
        "error_code": code,
    }
