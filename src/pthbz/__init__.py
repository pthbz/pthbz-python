"""
pthbz – Official Python SDK for the pth.bz URL shortener.

Features:
- Create short links (permanent HTTP 301).
- Get the interstitial (anti-bot) variant.
- Build QR PNG URLs with customizable size.
- Synchronous and asynchronous clients.
- CLI: `pthbz shorten https://example.com`

Author: Avel Kox
License: MIT
"""
from .client import PthBzClient
from .async_client import AsyncPthBzClient
from .models import ShortenResponse, ServiceLimits
from .exceptions import (
    PthBzError,
    ValidationError,
    RateLimitError,
    ApiHttpError,
    ApiBadRequest,
    ApiNotFound,
    ApiServerError,
)
from .validators import validate_and_canonicalize_url
from .utils import extract_code_from_url, build_qr_url

__all__ = [
    "PthBzClient",
    "AsyncPthBzClient",
    "ShortenResponse",
    "ServiceLimits",
    "PthBzError",
    "ValidationError",
    "RateLimitError",
    "ApiHttpError",
    "ApiBadRequest",
    "ApiNotFound",
    "ApiServerError",
    "validate_and_canonicalize_url",
    "extract_code_from_url",
    "build_qr_url",
]

__version__ = "1.0.4"
__author__ = "Avel Kox"
