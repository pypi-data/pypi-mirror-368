"""
Enhanced OpenAI Provider implementation.
"""

import logging
from typing import Any, List, Optional

logger = logging.getLogger(__name__)

# Use relative import to avoid circular imports
from ...types import LLMMessage, LLMResponse

# Import the base provider
from .base_provider import BaseLLMProvider

# Try to import optional dependencies
_openai_module = None
_openai_status = {"available": False}
try:
    import openai

    _openai_module = openai
    _openai_status["available"] = True
except ImportError:
    pass

# For backward compatibility
_OPENAI_AVAILABLE = _openai_status["available"]


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider with comprehensive error handling."""

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o-mini",
        **kwargs: Any,
    ):
        """Initialize OpenAI provider.

        Supports legacy "model_name" keyword for compatibility with examples.
        """
        # Backward-compat: map model_name -> model if provided
        model_compat = kwargs.pop("model_name", None)
        if model_compat and not model:
            model = model_compat  # type: ignore[assignment]

        super().__init__(model=model, **kwargs)
        self.api_key = api_key
        self.model = model

        # Check if OpenAI is available when using real implementation
        if not _OPENAI_AVAILABLE:
            logger.warning("OpenAI library not installed. Using mock implementation.")

    async def complete(
        self,
        messages: List[LLMMessage],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Complete a chat conversation."""
        # Use the chat_completion method
        return await self.chat_completion(messages, max_tokens, temperature, model, **kwargs)
    
    async def chat_completion(
        self,
        messages: List[LLMMessage],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Generate response from OpenAI."""
        if _openai_module and self.api_key:
            try:
                client = _openai_module.OpenAI(api_key=self.api_key)
                
                # Convert LLMMessage to dict format
                msg_dicts = [{"role": msg.role, "content": msg.content} for msg in messages]
                
                response = client.chat.completions.create(
                    model=model or self.model,
                    messages=msg_dicts,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs
                )
                
                return LLMResponse(
                    content=response.choices[0].message.content,
                    model=response.model,
                    provider="openai",
                    tokens_used=response.usage.total_tokens if response.usage else 0,
                    usage={
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0,
                    } if response.usage else {},
                )
            except Exception as e:
                logger.error(f"OpenAI API error: {e}")
                # Fallback to mock response
        
        # Mock response if OpenAI not available or error
        content = f"Mock response for: {messages[-1].content if messages else 'empty'}"
        return LLMResponse(
            content=content,
            model=model or self.model,
            provider="openai",
            tokens_used=50,
            usage={
                "prompt_tokens": 25,
                "completion_tokens": 25,
                "total_tokens": 50,
            },
        )
    
    async def generate_response(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        model: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Generate a simple text response."""
        messages = [LLMMessage(role="user", content=prompt)]
        response = await self.chat_completion(messages, max_tokens, temperature, model, **kwargs)
        return response.content
    
    async def stream_chat_completion(
        self,
        messages: List[LLMMessage],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        model: Optional[str] = None,
        **kwargs: Any,
    ):
        """Stream response from OpenAI."""
        if _openai_module and self.api_key:
            try:
                client = _openai_module.OpenAI(api_key=self.api_key)
                msg_dicts = [{"role": msg.role, "content": msg.content} for msg in messages]
                
                stream = client.chat.completions.create(
                    model=model or self.model,
                    messages=msg_dicts,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=True,
                    **kwargs
                )
                
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            except Exception as e:
                logger.error(f"OpenAI streaming error: {e}")
                yield f"Error: {str(e)}"
        else:
            # Mock streaming
            response = f"Mock streaming response for: {messages[-1].content if messages else 'empty'}"
            for word in response.split():
                yield word + " "
