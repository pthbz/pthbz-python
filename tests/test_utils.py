from __future__ import annotations
from pthbz.utils import extract_code_from_url, build_qr_url

def test_extract_code_variants():
    assert extract_code_from_url("https://host/AbC1234") == "AbC1234"
    assert extract_code_from_url("https://host/AbC1234.png") == "AbC1234"
    assert extract_code_from_url("https://host/i/AbC1234") == "AbC1234"
    assert extract_code_from_url("https://host/i/AbC1234.png") == "AbC1234"
    assert extract_code_from_url("https://host/?qr=AbC1234") == "AbC1234"
    assert extract_code_from_url("https://host/?qi=AbC1234") == "AbC1234"

def test_build_qr_url():
    assert build_qr_url("https://host", "AbC1234") == "https://host/?qr=AbC1234"
    assert build_qr_url("https://host", "AbC1234", interstitial=True) == "https://host/?qi=AbC1234"
    assert build_qr_url("https://host", "AbC1234", px=640) == "https://host/?qr=AbC1234&px=640"
