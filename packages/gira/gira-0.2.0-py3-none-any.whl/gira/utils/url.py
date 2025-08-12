"""URL and URI handling utilities.

This module provides helper functions for validating and manipulating URLs
used throughout the Gira project. The implementation focuses on the common
cases needed by the CLI and intentionally avoids heavy dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from ipaddress import ip_address
from typing import Iterable, Mapping
from urllib.parse import ParseResult, urlencode, urljoin, urlparse, urlunparse


@dataclass
class UrlComponents:
    """Simple container for parsed URL components."""

    scheme: str
    netloc: str
    path: str
    params: str
    query: str
    fragment: str

    @classmethod
    def from_url(cls, url: str) -> "UrlComponents":
        parsed = urlparse(url)
        return cls(*parsed)


def is_valid_url(url: str) -> bool:
    """Return True if ``url`` has an HTTP(S) scheme and a network location."""

    try:
        parsed = urlparse(url)
    except Exception:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def is_secure_url(url: str) -> bool:
    """Return True if ``url`` uses HTTPS."""

    return urlparse(url).scheme == "https"


def extract_domain(url: str) -> str:
    """Return the host portion of ``url`` (without credentials or port)."""

    return urlparse(url).hostname or ""


def is_allowed_domain(url: str, allowed_domains: Iterable[str]) -> bool:
    """Check if ``url``'s domain matches any in ``allowed_domains``.

    Supports wildcard patterns like ``*.example.com`` which match subdomains.
    """

    domain = extract_domain(url)
    for allowed in allowed_domains:
        if allowed.startswith("*."):
            suffix = allowed[2:]
            if domain == suffix or domain.endswith("." + suffix):
                return True
        elif domain == allowed:
            return True
    return False


def validate_webhook_url(url: str, allowed_domains: Iterable[str] | None = None) -> bool:
    """Validate a webhook URL.

    A valid webhook URL must:
    - be a valid URL
    - use HTTPS
    - match ``allowed_domains`` if provided
    """

    if not is_valid_url(url):
        return False
    if not is_secure_url(url):
        return False
    if allowed_domains and not is_allowed_domain(url, allowed_domains):
        return False
    return True


def parse_url(url: str) -> ParseResult:
    """Parse ``url`` and return :class:`urllib.parse.ParseResult`."""

    return urlparse(url)


def format_display_url(url: str, max_length: int = 50) -> str:
    """Return ``url`` truncated to ``max_length`` characters for display."""

    if len(url) <= max_length:
        return url
    return f"{url[: max_length - 3]}..."


def normalize_url(url: str) -> str:
    """Normalize ``url`` by lowercasing scheme/host and stripping trailing slash."""

    parsed = urlparse(url)
    path = parsed.path.rstrip("/")
    normalized = parsed._replace(scheme=parsed.scheme.lower(), netloc=parsed.netloc.lower(), path=path)
    return urlunparse(normalized)


def check_url_safety(url: str) -> bool:
    """Basic safety check to reject dangerous schemes and private networks."""

    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    return not is_private_network(url)


def is_private_network(url: str) -> bool:
    """Return True if ``url`` targets localhost or a private IP address."""

    host = extract_domain(url)
    if not host:
        return False
    if host == "localhost":
        return True
    try:
        ip = ip_address(host)
    except ValueError:
        return False
    return ip.is_private or ip.is_loopback


def sanitize_url(url: str) -> str:
    """Remove credentials from ``url`` for safe logging."""

    parsed = urlparse(url)
    netloc = parsed.netloc.split("@")[-1]
    sanitized = parsed._replace(netloc=netloc)
    return urlunparse(sanitized)


def build_query_string(params: Mapping[str, str]) -> str:
    """Build a query string from mapping of parameters."""

    return urlencode(params, doseq=True)


def merge_urls(base: str, path: str) -> str:
    """Combine ``base`` URL and ``path`` respecting URL semantics."""

    return urljoin(base, path)


def get_url_scheme(url: str) -> str:
    """Return the scheme component of ``url``."""

    return urlparse(url).scheme

