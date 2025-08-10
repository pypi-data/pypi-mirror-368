"""Legacy LLM compatibility namespace.

This module provides a stable import surface for tests and external code that
use the historical `llm.*` path. It re-exports objects from
`llamaagent.llm` to ensure backward compatibility.

Author: Nik Jois <nikjois@llamasearch.ai>
"""

from llamaagent.llm.factory import (
    LLMFactory,
    ProviderFactory,
    create_provider,
    get_available_providers,
    get_models_for_provider,
)

__all__ = [
    "LLMFactory",
    "ProviderFactory",
    "create_provider",
    "get_available_providers",
    "get_models_for_provider",
]


