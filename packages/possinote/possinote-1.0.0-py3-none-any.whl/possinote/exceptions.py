"""
Custom exceptions for the Possinote SDK.
"""


class PossinoteError(Exception):
    """Base exception for all Possinote SDK errors."""
    
    def __init__(self, message: str, code: int = None, response: dict = None):
        super().__init__(message)
        self.code = code
        self.response = response


class AuthenticationError(PossinoteError):
    """Raised when authentication fails (invalid API key)."""
    pass


class PaymentRequiredError(PossinoteError):
    """Raised when payment is required (insufficient credits)."""
    pass


class RateLimitError(PossinoteError):
    """Raised when rate limit is exceeded."""
    pass


class ValidationError(PossinoteError):
    """Raised when request validation fails."""
    pass


class APIError(PossinoteError):
    """Raised for general API errors."""
    pass
