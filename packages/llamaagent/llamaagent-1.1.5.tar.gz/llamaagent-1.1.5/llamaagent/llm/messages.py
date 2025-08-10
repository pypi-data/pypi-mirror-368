"""
Message and response structures for LLM providers.

Author: Nik Jois <nikjois@llamasearch.ai>
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

from ..types import LLMMessage, LLMResponse  # Re-export for compatibility


class MessageRole(Enum):
    """Enum for message roles in conversations."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


@dataclass
class Message:
    """Represents a message in a conversation."""

    role: MessageRole
    content: str
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


@dataclass
class StreamingResponse:
    """Represents a streaming response chunk."""

    chunk: str
    is_final: bool = False
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata: Dict[str, Any] = {}


__all__ = [
    "LLMMessage",
    "LLMResponse",
    "StreamingResponse",
    "Message",
    "MessageRole",
]
