"""Knowledge module for LlamaAgent.

Provides minimal KnowledgeGenerator compatibility for tests.
"""

from typing import Any, Dict, List


class KnowledgeBase:
    """Basic knowledge base."""

    def __init__(self):
        self.knowledge = {}

    def add(self, key: str, value: Any) -> None:
        """Add knowledge."""
        self.knowledge[key] = value

    def get(self, key: str) -> Any:
        """Get knowledge."""
        return self.knowledge.get(key)


class KnowledgeGenerator:
    """Minimal stub used by tests to generate knowledge entries."""

    def generate(self, items: List[str]) -> Dict[str, Any]:
        return {str(i): item for i, item in enumerate(items)}


__all__ = ['KnowledgeBase', 'KnowledgeGenerator']
