"""
Utility functions
"""

import time
import json
from typing import Dict, Any, Generator


def exponential_backoff(attempt: int, base: int = 2, max_time: int = 60) -> int:
    """Calculate exponential backoff time"""
    wait_time = min(base ** attempt, max_time)
    return wait_time


def parse_streaming_line(line: str) -> Dict[str, Any]:
    """Parse a streaming response line"""
    if not line.startswith('data: '):
        return None
    
    chunk_data = line[6:].strip()
    if chunk_data == '[DONE]':
        return {'done': True}
    
    try:
        return json.loads(chunk_data)
    except json.JSONDecodeError:
        return None


def validate_messages(messages: list) -> bool:
    """Validate message format"""
    if not messages:
        return False
    
    for message in messages:
        if not isinstance(message, dict):
            return False
        if 'role' not in message or 'content' not in message:
            return False
        if message['role'] not in ['system', 'user', 'assistant']:
            return False
    
    return True


def sanitize_api_key(api_key: str) -> str:
    """Sanitize API key for logging"""
    if not api_key or len(api_key) < 10:
        return "***"
    return f"{api_key[:4]}...{api_key[-4:]}"
