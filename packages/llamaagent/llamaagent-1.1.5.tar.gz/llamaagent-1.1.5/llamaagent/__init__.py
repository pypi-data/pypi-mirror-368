"""LlamaAgent: Advanced LLM Agent Framework

A comprehensive framework for building intelligent agents with SPRE optimization,
vector memory, and extensive tool integration.

Author: Nik Jois <nikjois@llamasearch.ai>
"""

import warnings

from . import tools as tools  # ensure package exposes tools attribute
from ._version import __version__
from .agents import ReactAgent
from .agents.base import AgentConfig, AgentRole
from .llm import LLMFactory, LLMMessage, LLMResponse, create_provider
from .tools import ToolRegistry, get_all_tools

# Suppress SSL/OpenSSL warnings in environments with LibreSSL (GitHub/macOS)
warnings.filterwarnings("ignore", message="urllib3 v2 only supports OpenSSL")
warnings.filterwarnings("ignore", message="NotOpenSSLWarning")

__all__ = [
    "__version__",
    "ReactAgent",
    "AgentConfig",
    "AgentRole",
    "LLMFactory",
    "LLMMessage",
    "LLMResponse",
    "create_provider",
    "ToolRegistry",
    "get_all_tools",
    "tools",
]

# Optional modules (ignore errors at import time)
try:  # pragma: no cover
    from .core.orchestrator import DistributedOrchestrator  # type: ignore

    AgentOrchestrator = DistributedOrchestrator
    __all__.extend(["AgentOrchestrator", "DistributedOrchestrator"])
except Exception:
    pass

try:  # pragma: no cover
    from . import integration

    __all__.append("integration")
except ImportError:
    pass

