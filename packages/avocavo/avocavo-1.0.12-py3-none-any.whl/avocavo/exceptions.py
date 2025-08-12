"""
Exception classes for Avocavo Nutrition API
"""


class ApiError(Exception):
    """Base exception for API errors"""
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        self.message = message
        self.status_code = status_code
        self.response = response or {}
        super().__init__(self.message)


class AuthenticationError(ApiError):
    """Authentication and authorization errors"""
    pass


class RateLimitError(ApiError):
    """Rate limit exceeded errors"""
    def __init__(self, message: str, limit: int = None, usage: int = None, **kwargs):
        self.limit = limit
        self.usage = usage
        super().__init__(message, **kwargs)


class ValidationError(ApiError):
    """Request validation errors"""
    pass


class ServiceUnavailableError(ApiError):
    """Service temporarily unavailable"""
    pass