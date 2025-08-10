import asyncio

import pytest

from llamaagent.llm.providers.openai_provider import OpenAIProvider
from llamaagent.types import LLMMessage


@pytest.mark.asyncio
async def test_openai_provider_mock_path():
    provider = OpenAIProvider(api_key="test-key", model="gpt-4o-mini")
    messages = [LLMMessage(role="user", content="Hello")]
    resp = await provider.complete(messages)
    assert isinstance(resp.content, str)
    assert resp.provider == "openai"
    assert resp.tokens_used > 0

