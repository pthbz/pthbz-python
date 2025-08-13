class PthBzError(Exception):
    """Base error for the pthbz SDK."""


class ValidationError(PthBzError):
    """Validation error (e.g., invalid URL)."""


class ApiHttpError(PthBzError):
    """HTTP error returned by the API."""

    def __init__(self, status_code: int, payload: dict | None = None, message: str | None = None):
        self.status_code = status_code
        self.payload = payload
        self.message = message or (payload.get("error") if isinstance(payload, dict) else None) or "HTTP error"
        super().__init__(f"{self.status_code}: {self.message}")


class ApiBadRequest(ApiHttpError):
    """400 Bad Request."""


class RateLimitError(ApiHttpError):
    """429 Too Many Requests."""


class ApiNotFound(ApiHttpError):
    """404 Not Found."""


class ApiServerError(ApiHttpError):
    """5xx Server Error."""
