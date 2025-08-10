"""Evolution and learning modules for LlamaAgent.

Provides backward-compatibility exports used by tests.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .knowledge_base import CooperationKnowledge as KnowledgeBase
from .reflection import ReflectionModule as ReflectionEngine


@dataclass
class EvolutionOrchestrator:
    """Thin orchestrator facade used by tests.

    This minimal implementation delegates to `ReflectionEngine` and
    `KnowledgeBase` to provide a stable API surface for test imports.
    """

    knowledge: KnowledgeBase = KnowledgeBase()
    reflection: ReflectionEngine = ReflectionEngine()

    def evolve(self, inputs: List[str], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        report = {
            "inputs": inputs,
            "reflections": [self.reflection.reflect(text) for text in inputs],
            "metadata": metadata or {},
        }
        self.knowledge.add_entries(inputs)
        return report


__all__ = [
    "KnowledgeBase",
    "ReflectionEngine",
    "EvolutionOrchestrator",
]
