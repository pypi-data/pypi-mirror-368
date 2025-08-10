import os

from llamaagent.memory import MemoryManager


def test_memory_manager_sqlite_backend(tmp_path):
    os.environ["LLAMAAGENT_MEMORY_BACKEND"] = "sqlite"
    os.environ["LLAMAAGENT_MEMORY_PATH"] = str(tmp_path / "mem.db")
    mm = MemoryManager()
    mm.store("k1", {"v": 1})
    val = mm.retrieve("k1")
    assert val == {"v": 1}
    # cleanup should not raise
    import asyncio

    asyncio.get_event_loop().run_until_complete(mm.cleanup())

