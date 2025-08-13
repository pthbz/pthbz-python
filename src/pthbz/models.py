from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ShortenResponse:
    short_url_301: str
    short_url_js: str
    qr_301_png_url: str
    qr_js_png_url: str

@dataclass(frozen=True)
class ServiceLimits:
    requests_per_window: int = 30
    window_seconds: int = 600
    max_url_length: int = 2000
