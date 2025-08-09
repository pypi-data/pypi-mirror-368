"""
Custom exceptions for the Promptlyzer client library.

This module defines all custom exceptions that can be raised by the
Promptlyzer client during API interactions.
"""

from typing import Optional
import requests
import re


class PromptlyzerError(Exception):
    """
    Base exception class for all Promptlyzer client errors.
    
    Attributes:
        message: Human-readable error message
        http_status: HTTP status code if applicable
        response: Original response object if available
    """
    
    def __init__(
        self, 
        message: Optional[str] = None, 
        http_status: Optional[int] = None, 
        response: Optional[requests.Response] = None
    ):
        """
        Initialize the exception.
        
        Args:
            message: Error message
            http_status: HTTP status code
            response: Original HTTP response object
        """
        # Sanitize message to remove sensitive data
        self.message = self._sanitize_message(message or "An error occurred with the Promptlyzer API")
        self.http_status = http_status
        self.response = response
        super().__init__(self.message)
    
    def _sanitize_message(self, message: str) -> str:
        """Remove sensitive information from error messages."""
        # Remove potential API keys
        message = re.sub(r'(pk_live_|pk_test_|sk_)[A-Za-z0-9]{20,}', '[REDACTED_API_KEY]', message)
        # Remove potential tokens
        message = re.sub(r'Bearer\s+[A-Za-z0-9\-._~+/]+=*', 'Bearer [REDACTED_TOKEN]', message)
        # Remove email addresses
        message = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[REDACTED_EMAIL]', message)
        # Remove URLs with potential sensitive params
        message = re.sub(r'(https?://[^\s]+api_key=[^\s&]+)', '[REDACTED_URL]', message)
        return message
    
    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.http_status:
            return f"[{self.http_status}] {self.message}"
        return self.message


class AuthenticationError(PromptlyzerError):
    """
    Raised when authentication fails.
    
    This can occur when:
    - Invalid API key is provided
    - API key is missing
    - JWT token is expired (legacy)
    - No authentication credentials provided
    """
    pass


class ResourceNotFoundError(PromptlyzerError):
    """
    Raised when a requested resource is not found.
    
    This can occur when:
    - Project doesn't exist
    - Prompt doesn't exist
    - Team doesn't exist
    - Invalid resource ID is provided
    """
    pass


class ValidationError(PromptlyzerError):
    """
    Raised when request validation fails.
    
    This can occur when:
    - Required fields are missing
    - Invalid field values are provided
    - Data format is incorrect
    """
    pass


class ServerError(PromptlyzerError):
    """
    Raised when the server encounters an error.
    
    This typically indicates:
    - Internal server errors (500)
    - Service unavailable (503)
    - Gateway timeout (504)
    """
    pass


class RateLimitError(PromptlyzerError):
    """
    Raised when API rate limit is exceeded.
    
    The error message will typically include:
    - Current rate limit
    - Time until limit resets
    - Retry-after header value
    """
    pass


class InferenceError(PromptlyzerError):
    """
    Raised when inference operation fails.
    
    This can occur when:
    - Provider API is unavailable
    - Invalid model specified
    - Provider returns an error
    - Timeout during inference
    """
    pass