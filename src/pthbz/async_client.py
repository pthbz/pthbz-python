from __future__ import annotations
import json
import httpx

from .models import ShortenResponse, ServiceLimits
from .exceptions import (
    ApiBadRequest,
    ApiHttpError,
    ApiNotFound,
    ApiServerError,
    RateLimitError,
)
from .validators import validate_and_canonicalize_url

class AsyncPthBzClient:
    """
    Asynchronous client for pth.bz using httpx.

    Example:
        async with AsyncPthBzClient() as client:
            res = await client.shorten("https://example.com")
            print(res.short_url_301)

    Parameters:
        base_url: service base URL (e.g., "https://pth.bz").
        timeout: request timeout in seconds.
        limits: service limits (used for local URL length validation).
        client: external httpx.AsyncClient (optional).
    """

    def __init__(
        self,
        base_url: str = "https://pth.bz",
        timeout: float = 10.0,
        limits: ServiceLimits | None = None,
        client: httpx.AsyncClient | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = float(timeout)
        self.limits = limits or ServiceLimits()
        self._external_client = client
        self._client: httpx.AsyncClient | None = None

        self._headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def __aenter__(self) -> "AsyncPthBzClient":
        if self._external_client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        else:
            self._client = self._external_client
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._external_client is None and self._client is not None:
            await self._client.aclose()

    async def shorten(self, url: str) -> ShortenResponse:
        """Create a short link and return ShortenResponse (301 + interstitial anti-bot + QR PNG)."""
        canon = validate_and_canonicalize_url(url, self.limits)
        endpoint = f"{self.base_url}/api/shorten"

        client = self._client or self._external_client
        if client is None:
            async with httpx.AsyncClient(timeout=self.timeout) as tmp:
                resp = await tmp.post(endpoint, data=json.dumps({"url": canon}), headers=self._headers)
        else:
            resp = await client.post(endpoint, data=json.dumps({"url": canon}), headers=self._headers)

        return self._handle_response(resp)

    def _handle_response(self, resp: httpx.Response) -> ShortenResponse:
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
