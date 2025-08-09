"""
Custom exceptions for DD API Client
"""

class APIError(Exception):
    """Base exception for API errors"""
    
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
    
    def __str__(self):
        if self.status_code:
            return f"APIError ({self.status_code}): {self.message}"
        return f"APIError: {self.message}"


class RateLimitError(APIError):
    """Raised when rate limit is exceeded"""
    pass


class AuthenticationError(APIError):
    """Raised when authentication fails"""
    pass


class ValidationError(APIError):
    """Raised when request validation fails"""
    pass


class TimeoutError(APIError):
    """Raised when request times out"""
    pass
