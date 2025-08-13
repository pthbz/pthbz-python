from __future__ import annotations
import pytest
from pthbz.validators import validate_and_canonicalize_url
from pthbz.exceptions import ValidationError

def test_valid_http():
    assert validate_and_canonicalize_url("http://example.com/path") == "http://example.com/path"

def test_add_scheme():
    assert validate_and_canonicalize_url("example.com") == "http://example.com/"

def test_requires_dot_or_ip_or_localhost():
    with pytest.raises(ValidationError):
        validate_and_canonicalize_url("http://invalidhost")

    assert validate_and_canonicalize_url("http://127.0.0.1") == "http://127.0.0.1/"
    assert validate_and_canonicalize_url("http://localhost") == "http://localhost/"

def test_reject_userinfo():
    with pytest.raises(ValidationError):
        validate_and_canonicalize_url("http://user:pass@example.com")

def test_reject_unsupported_scheme():
    with pytest.raises(ValidationError):
        validate_and_canonicalize_url("ftp://example.com")
