from __future__ import annotations
import json
from typing import Any, Dict
import requests

from .models import ShortenResponse, ServiceLimits
from .exceptions import (
    ApiBadRequest,
    ApiHttpError,
    ApiNotFound,
    ApiServerError,
    RateLimitError,
)
from .validators import validate_and_canonicalize_url

class PthBzClient:
    """
    Synchronous client for pth.bz.

    Example:
        client = PthBzClient()  # default base URL
        res = client.shorten("https://example.com")
        print(res.short_url_301, res.short_url_js)

    Parameters:
        base_url: service base URL (e.g., "https://pth.bz" or your branded domain).
        timeout: request timeout in seconds.
        limits: service limits (used for local URL length validation).
        session: optional requests.Session.
    """

    def __init__(
        self,
        base_url: str = "https://pth.bz",
        timeout: float = 10.0,
        limits: ServiceLimits | None = None,
        session: requests.Session | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = float(timeout)
        self.limits = limits or ServiceLimits()
        self._session = session or requests.Session()

        self._headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def close(self) -> None:
        try:
            self._session.close()
        except Exception:
            pass

    def shorten(self, url: str) -> ShortenResponse:
        """Create a short link and return ShortenResponse (301 + interstitial anti-bot + QR PNG)."""
        canon = validate_and_canonicalize_url(url, self.limits)
        endpoint = f"{self.base_url}/api/shorten"

        resp = self._session.post(
            endpoint,
            data=json.dumps({"url": canon}),
            headers=self._headers,
            timeout=self.timeout,
        )
        return self._handle_response(resp)

    def _handle_response(self, resp: requests.Response) -> ShortenResponse:
        status = resp.status_code
        try:
            payload = resp.json()
        except Exception:
            payload = None

        if status == 200 and isinstance(payload, dict):
            for key in ("short_url_301", "short_url_js", "qr_301_png_url", "qr_js_png_url"):
                if key not in payload or not isinstance(payload[key], str):
                    raise ApiHttpError(status, payload, f"Invalid payload: missing '{key}'")
            return ShortenResponse(
                short_url_301=payload["short_url_301"],
                short_url_js=payload["short_url_js"],
                qr_301_png_url=payload["qr_301_png_url"],
                qr_js_png_url=payload["qr_js_png_url"],
            )

        if status == 400:
            raise ApiBadRequest(status, payload)
        if status == 404:
            raise ApiNotFound(status, payload)
        if status == 429:
            raise RateLimitError(status, payload)
        if 500 <= status <= 599:
            raise ApiServerError(status, payload)

        raise ApiHttpError(status, payload)
