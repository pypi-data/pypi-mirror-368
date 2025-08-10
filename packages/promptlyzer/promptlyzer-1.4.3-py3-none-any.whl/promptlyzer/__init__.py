"""
Promptlyzer Python Client

A comprehensive client library for the Promptlyzer API, providing:
- Prompt management with caching
- Multi-provider LLM inference
- API key and JWT authentication
- Automatic prompt updates
- Cost and performance tracking

Installation:
    pip install promptlyzer

Basic Usage:
    >>> from promptlyzer import PromptlyzerClient
    >>> client = PromptlyzerClient(api_key="pk_live_...")
    >>> prompt = client.get_prompt("project-id", "greeting")
    >>> print(prompt['content'])

For more information, visit: https://docs.promptlyzer.com
"""

from .client import PromptlyzerClient
from .prompt_manager import PromptManager
from .exceptions import (
    PromptlyzerError, 
    AuthenticationError, 
    ResourceNotFoundError,
    ValidationError,
    ServerError,
    RateLimitError,
    InferenceError
)

__version__ = "1.4.3"
__author__ = "Promptlyzer Team"
__email__ = "contact@promptlyzer.com"
__license__ = "MIT"

__all__ = [
    # Main classes
    "PromptlyzerClient",
    "PromptManager",
    
    # Exceptions
    "PromptlyzerError",
    "AuthenticationError", 
    "ResourceNotFoundError",
    "ValidationError",
    "ServerError",
    "RateLimitError",
    "InferenceError",
    
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__"
]