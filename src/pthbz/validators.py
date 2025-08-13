from __future__ import annotations
import re
import ipaddress
from urllib.parse import urlparse, urlunparse
try:
    import idna
except ImportError:
    idna = None  # optional but recommended

from .exceptions import ValidationError
from .models import ServiceLimits

_SCHEME_RE = re.compile(r"^[a-z][a-z0-9+\-.]*://", re.IGNORECASE)
_LABEL_RE = re.compile(r"^[A-Za-z0-9-]{1,63}$")

def _has_dot(host: str) -> bool:
    return "." in host

def _is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False

def _punycode(host: str) -> str:
    if idna is None:
        return host.lower()
    try:
        return idna.encode(host, uts46=True).decode("ascii")
    except Exception as exc:
        raise ValidationError("Host name is invalid.") from exc

def validate_and_canonicalize_url(raw: str, limits: ServiceLimits | None = None) -> str:
    """
    Validate and canonicalize a URL according to server-aligned rules:
    - Only http/https are allowed.
    - IP and localhost are allowed without a dot; other hosts must contain at least one dot.
    - Userinfo is forbidden.
    - Length must not exceed MAX_URL_LENGTH.
    - Fragment (#...) is removed.
    - IDN → punycode (if `idna` is installed).
    """
    limits = limits or ServiceLimits()
    if raw is None:
        raise ValidationError("Please enter a URL.")

    s = raw.strip().replace("\x00", "").replace("\x1F", "")
    if not s:
        raise ValidationError("Please enter a URL.")

    if not _SCHEME_RE.match(s):
        s = "http://" + s

    if len(s) > limits.max_url_length:
        raise ValidationError(f"The link is too long. Please use a URL shorter than {limits.max_url_length} characters.")

    parsed = urlparse(s)
    if not parsed.scheme or not parsed.netloc:
        raise ValidationError("URL is missing scheme or host.")

    scheme = parsed.scheme.lower()
    if scheme not in ("http", "https"):
        raise ValidationError("Only http:// and https:// links are allowed.")

    if parsed.username is not None or parsed.password is not None:
        raise ValidationError("User info in URL is not allowed.")

    host = (parsed.hostname or "").lower()
    if not host:
        raise ValidationError("URL is missing host.")

    is_ip = _is_ip(host)
    is_localhost = host == "localhost"

    if not is_ip and not is_localhost:
        host_ascii = _punycode(host)
        if not _has_dot(host_ascii):
            raise ValidationError("Host must include a dot (e.g., example.com).")
        labels = host_ascii.split(".")
        for label in labels:
            if not _LABEL_RE.match(label):
                raise ValidationError("Host contains invalid characters.")
            if label.startswith("-") or label.endswith("-"):
                raise ValidationError("Host labels cannot start or end with a hyphen.")
        if len(host_ascii) > 253:
            raise ValidationError("Host is too long.")
    else:
        host_ascii = host

    path = parsed.path or "/"
    query = parsed.query or ""
    port_part = f":{parsed.port}" if parsed.port else ""

    canonical = urlunparse((scheme, host_ascii + port_part, path, "", query, ""))

    return canonical
