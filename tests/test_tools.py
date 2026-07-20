import pytest

from ologos_aioc import Tool, ToolRegistry


def _add(a: int, b: int) -> int:
    return a + b


def test_register_and_execute():
    registry = ToolRegistry()
    registry.register(Tool(
        name="add",
        description="Add two integers",
        parameters={"type": "object", "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}}},
        handler=_add,
    ))
    assert len(registry) == 1
    assert "add" in registry
    assert registry.execute("add", {"a": 2, "b": 3}) == 5


def test_schemas_shape():
    registry = ToolRegistry()
    registry.register(Tool(
        name="add", description="Add two integers",
        parameters={"type": "object", "properties": {}}, handler=_add,
    ))
    schemas = registry.schemas()
    assert schemas == [{
        "type": "function",
        "function": {"name": "add", "description": "Add two integers", "parameters": {"type": "object", "properties": {}}},
    }]


def test_execute_unknown_raises():
    registry = ToolRegistry()
    with pytest.raises(KeyError):
        registry.execute("nope", {})
