"""Memory module for LlamaAgent."""

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .base import BaseMemory, SimpleMemory


@dataclass
class MemoryEntry:
    """A single memory entry."""

    content: str
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: float = field(default_factory=time.time)


class MemoryManager:
    """Basic memory manager with optional SQLite persistence.

    Default backend is in-process dict. Set environment variable
    `LLAMAAGENT_MEMORY_BACKEND=sqlite` to enable SQLite persistence.
    Use `LLAMAAGENT_MEMORY_PATH` to control the database file path.
    """

    def __init__(self):
        import os

        self._backend = os.getenv("LLAMAAGENT_MEMORY_BACKEND", "memory").lower()
        self.memory: dict[str, Any] = {}
        self._conn = None
        self._cursor = None

        if self._backend == "sqlite":
            import sqlite3

            path = os.getenv("LLAMAAGENT_MEMORY_PATH", "./llamaagent_memory.db")
            self._conn = sqlite3.connect(path)
            self._cursor = self._conn.cursor()
            self._cursor.execute(
                "CREATE TABLE IF NOT EXISTS kv_store (k TEXT PRIMARY KEY, v BLOB)"
            )
            self._conn.commit()

    def store(self, key: str, value: Any) -> None:
        """Store a value in memory."""
        if self._backend == "sqlite" and self._cursor is not None:
            import json

            self._cursor.execute(
                "INSERT INTO kv_store(k, v) VALUES(?, ?) ON CONFLICT(k) DO UPDATE SET v=excluded.v",
                (key, json.dumps(value)),
            )
            self._conn.commit()  # type: ignore[union-attr]
            return
        self.memory[key] = value

    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a value from memory."""
        if self._backend == "sqlite" and self._cursor is not None:
            import json

            row = self._cursor.execute("SELECT v FROM kv_store WHERE k=?", (key,)).fetchone()
            if row:
                try:
                    return json.loads(row[0])
                except Exception:
                    return row[0]
            return None
        return self.memory.get(key)

    async def cleanup(self) -> None:
        """Cleanup memory resources."""
        self.memory.clear()
        if self._cursor is not None:
            try:
                self._cursor.close()
            except Exception:
                pass
        if self._conn is not None:
            try:
                self._conn.close()
            except Exception:
                pass


__all__ = ['MemoryManager', 'MemoryEntry', 'SimpleMemory', 'BaseMemory']
