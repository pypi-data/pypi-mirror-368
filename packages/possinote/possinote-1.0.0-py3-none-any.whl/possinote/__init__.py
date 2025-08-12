"""
Possinote Python SDK

Official Python SDK for the PossiNote API - Send SMS, emails, and schedule messages with ease.
"""

from .client import Client
from .exceptions import (
    PossinoteError,
    AuthenticationError,
    PaymentRequiredError,
    RateLimitError,
    ValidationError,
    APIError,
)

class Possinote:
    """Main Possinote client class."""
    
    def __init__(self, api_key: str):
        self.client = Client(api_key=api_key)
        self.sms = self.client.sms
        self.email = self.client.email
        self.scheduling = self.client.scheduling

__version__ = "1.0.0"
__all__ = [
    "Possinote",
    "Client",
    "PossinoteError",
    "AuthenticationError",
    "PaymentRequiredError",
    "RateLimitError",
    "ValidationError",
    "APIError",
]
