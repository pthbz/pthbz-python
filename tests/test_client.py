from __future__ import annotations
import json
from pthbz.client import PthBzClient
from pthbz.models import ShortenResponse
from pthbz.exceptions import ApiBadRequest, RateLimitError
import requests
from requests.models import Response

class _DummyResp(Response):
    def __init__(self, code: int, payload: dict | None):
        super().__init__()
        self._content = json.dumps(payload or {}).encode("utf-8")
        self.status_code = code

class _DummySession(requests.Session):
    def __init__(self, response: Response):
        super().__init__()
        self._response = response
    def post(self, *a, **kw):
        return self._response

def test_shorten_ok():
    payload = {
        "short_url_301": "https://pth.bz/AbC1234",
        "short_url_js": "https://pth.bz/i/AbC1234",
        "qr_301_png_url": "https://pth.bz/?qr=AbC1234",
        "qr_js_png_url": "https://pth.bz/?qi=AbC1234",
    }
    session = _DummySession(_DummyResp(200, payload))
    c = PthBzClient(session=session)
    res = c.shorten("https://example.com")
    assert isinstance(res, ShortenResponse)
    assert res.short_url_js.endswith("/i/AbC1234")

def test_shorten_bad_request():
    session = _DummySession(_DummyResp(400, {"error": "Invalid URL"}))
    c = PthBzClient(session=session)
    try:
        c.shorten("notaurl")
    except ApiBadRequest as e:
        assert e.status_code == 400

def test_shorten_rate_limit():
    session = _DummySession(_DummyResp(429, {"error": "Too many requests"}))
    c = PthBzClient(session=session)
    try:
        c.shorten("https://example.com")
    except RateLimitError as e:
        assert e.status_code == 429
