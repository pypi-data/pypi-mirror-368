"""CLI module for LlamaAgent.

Author: Nik Jois <nikjois@llamasearch.ai>
"""

# Delegate to the Typer-based CLI for a unified interface
from .main import main  # noqa: F401

__all__ = ["main"]
