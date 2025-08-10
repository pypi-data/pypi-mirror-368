from llamaagent.tools.base import ToolRegistry, ToolParameterSpec, ToolResultSpec
from llamaagent.tools.calculator import CalculatorTool


def test_tool_registry_schema():
    reg = ToolRegistry()
    calc = CalculatorTool()
    params = [
        ToolParameterSpec(name="expression", type="string", required=True, description="Math expression"),
    ]
    result = ToolResultSpec(type="string", description="Result text")

    # Register with schema
    reg.register_with_schema(calc, params=params, result=result)

    # Validate
    schema = reg.get_schema(calc.name)
    assert schema is not None
    assert len(schema["params"]) == 1
    assert schema["result"].type == "string"

