from llamaagent.tools import ToolManager
from llamaagent.tools.base import ToolRegistry


def test_tool_manager_is_registry_alias():
    tm = ToolManager()
    assert isinstance(tm, ToolRegistry)

