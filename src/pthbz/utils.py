from __future__ import annotations
import re
from urllib.parse import urlparse, parse_qs

_CODE_RE = re.compile(r"/([A-Za-z0-9]{1,32})(?:\.png)?$")

def extract_code_from_url(short_url: str) -> str | None:
    """Extract CODE from various short URL shapes:
    - https://host/AbC1234
    - https://host/i/AbC1234
    - https://host/AbC1234.png
    - https://host/i/AbC1234.png
    - https://host/?qr=AbC1234
    - https://host/?qi=AbC1234
    """
    if not short_url:
        return None
    parsed = urlparse(short_url)
    qs = parse_qs(parsed.query or "")
    if "qr" in qs and qs["qr"]:
        return qs["qr"][0]
    if "qi" in qs and qs["qi"]:
        return qs["qi"][0]
    m = _CODE_RE.search(parsed.path or "")
    if m:
        return m.group(1)
    if parsed.path and parsed.path.startswith("/i/"):
        tail = parsed.path[len("/i/"):]
        tail = tail[:-4] if tail.endswith(".png") else tail
        if re.fullmatch(r"[A-Za-z0-9]{1,32}", tail or ""):
            return tail
    return None

def build_qr_url(base_url: str, code: str, interstitial: bool = False, px: int | None = None) -> str:
    """Build QR PNG URL:
      - 301:          {base}/?qr=CODE
      - interstitial: {base}/?qi=CODE
    Optionally set px size (200–2048).
    """
    path = "/?qi=" + code if interstitial else "/?qr=" + code
    if px is not None:
        if not (200 <= px <= 2048):
            raise ValueError("px must be in range 200..2048")
        path += f"&px={px}"
    return base_url.rstrip("/") + path
