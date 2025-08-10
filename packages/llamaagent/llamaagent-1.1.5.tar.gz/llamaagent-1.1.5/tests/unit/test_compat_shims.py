import asyncio

from llamaagent.tools.calculator import CalculatorTool
from llamaagent.llm.factory import LLMFactory
from llamaagent.agents.base import AgentConfig, BaseAgent
from llamaagent.types import TaskInput


async def test_calculator_async_execute_and_info():
    tool = CalculatorTool()
    out = await tool.execute(expression="2+3*4")
    assert out == "14" or out.endswith("14")
    info = tool.get_info()
    assert info["name"] == tool.name


def test_llm_factory_list_providers():
    factory = LLMFactory()
    providers = factory.list_providers()
    assert isinstance(providers, list)
    assert "mock" in providers


async def test_baseagent_execute_task_shim():
    agent = BaseAgent(config=AgentConfig(name="ShimAgent"))
    task = TaskInput(id="t1", data={"prompt": "hello"})
    res = await agent.execute_task(task)
    assert getattr(res, "status") in ("completed", "failed")


def test_taskinput_defaults_and_data():
    t = TaskInput(id="x1", data={"prompt": "p"})
    assert t.task == ""
    assert t.data == {"prompt": "p"}


def run():
    asyncio.run(test_calculator_async_execute_and_info())
    asyncio.run(test_baseagent_execute_task_shim())


if __name__ == "__main__":
    run()

