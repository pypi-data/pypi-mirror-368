"""
DD API Client - OpenAI-like Python client
"""

from .client import PromptOptimizers
from .exceptions import APIError, RateLimitError, AuthenticationError, ValidationError, TimeoutError
from .models import ChatCompletion, Message, Choice, Usage
from .constants import DEFAULT_BASE_URL, AVAILABLE_MODELS

__version__ = "1.0.0"
__author__ = "Your Name"

__all__ = [
    'PromptOptimizers',
    'APIError',
    'RateLimitError', 
    'AuthenticationError',
    'ValidationError',
    'TimeoutError',
    'ChatCompletion',
    'Message',
    'Choice',
    'Usage'
]

# Convenience function
def create_client(api_key: str = None, **kwargs) -> PromptOptimizers:
    """Create a new API client instance"""
    return PromptOptimizers(api_key=api_key, **kwargs)
