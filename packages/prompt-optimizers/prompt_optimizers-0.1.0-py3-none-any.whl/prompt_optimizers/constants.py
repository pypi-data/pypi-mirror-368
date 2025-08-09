"""
Constants and configuration
"""

# API Configuration
DEFAULT_BASE_URL = "https://api.prompt-optimizers.com/v1"
DEFAULT_TIMEOUT = 60
DEFAULT_MAX_RETRIES = 3

# Rate Limiting
RATE_LIMIT_BACKOFF_BASE = 2
MAX_BACKOFF_TIME = 60

# Headers
USER_AGENT = "PromptOptimizersClient/1.0.0"
CONTENT_TYPE = "application/json"

# Models
AVAILABLE_MODELS = [
    "gpt-4",
    "gpt-3.5-turbo",
    "gpt-4-turbo",
    "claude-3-opus",
    "claude-3-sonnet",
    "claude-3-haiku",
]

# Default Parameters
DEFAULT_MAX_TOKENS = 1000
DEFAULT_TEMPERATURE = 0.7
