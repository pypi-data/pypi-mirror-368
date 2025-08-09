from typing import List
from dataclasses import dataclass

@dataclass
class Usage:
    """Token usage information"""
    original_prompt_tokens: int
    optimized_prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    saving: float

@dataclass
class Message:
    """Chat message structure"""
    role: str
    content: str

@dataclass
class Choice:
    """Response choice structure"""
    index: int
    message: Message
    finish_reason: str

@dataclass
class ChatCompletion:
    """Chat completion response"""
    id: str
    object: str
    created: int
    model: str
    choices: List[Choice]
    usage: Usage