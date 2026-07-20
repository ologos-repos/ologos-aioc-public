from typing import Any

import pytest

from ologos_aioc import (
    EchoProvider,
    GovernanceHook,
    ModelCatalog,
    Orchestrator,
    Tool,
    ToolRegistry,
)
from ologos_aioc.orchestrator import MaxIterationsExceeded
from ologos_aioc.providers import ModelProvider, ModelResponse, ToolCall


def _catalog_entry(provider):
    catalog = ModelCatalog()
    catalog.register("m", provider)
    return catalog.get("m")


def test_simple_run_no_tools():
    orchestrator = Orchestrator(model=_catalog_entry(EchoProvider(canned_text="hello")))
    result = orchestrator.run("hi there")
    assert result.text == "hello"
    assert result.iterations == 1
    assert result.tool_calls_made == []


def test_tool_calling_loop_executes_tool_and_terminates():
    calls: list[dict] = []

    def weather(**kwargs):
        calls.append(kwargs)
        return "72F and sunny"

    tools = ToolRegistry()
    tools.register(Tool(
        name="weather", description="Get the weather",
        parameters={"type": "object", "properties": {}}, handler=weather,
    ))

    orchestrator = Orchestrator(model=_catalog_entry(EchoProvider()), tools=tools)
    result = orchestrator.run("call weather please")

    assert len(calls) == 1  # the tool was actually invoked, not just described
    assert len(result.tool_calls_made) == 1
    assert result.tool_calls_made[0].name == "weather"
    assert "72F and sunny" in result.text
    assert result.iterations == 2  # one tool round, one final-answer round


class _AlwaysToolCallProvider(ModelProvider):
    """A pathological provider that never stops calling a tool — exercises
    the iteration cap / runaway-loop backstop."""

    def complete(self, messages, tools=None):
        return ModelResponse(tool_calls=[ToolCall(id="x", name="noop", arguments={})])


def test_max_iterations_exceeded():
    tools = ToolRegistry()
    tools.register(Tool(name="noop", description="does nothing", parameters={"type": "object", "properties": {}}, handler=lambda: "ok"))
    orchestrator = Orchestrator(model=_catalog_entry(_AlwaysToolCallProvider()), tools=tools)
    with pytest.raises(MaxIterationsExceeded):
        orchestrator.run("loop forever", max_tool_iterations=3)


class _BlockingGovernanceHook(GovernanceHook):
    def __init__(self):
        self.before_calls = 0
        self.after_calls = 0

    def before_dispatch(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        self.before_calls += 1
        if any("forbidden" in m.get("content", "") for m in messages):
            raise PermissionError("blocked by policy")
        return messages

    def after_dispatch(self, messages, response_text):
        self.after_calls += 1
        return f"[reviewed] {response_text}"


def test_governance_hook_runs_before_and_after():
    hook = _BlockingGovernanceHook()
    orchestrator = Orchestrator(model=_catalog_entry(EchoProvider(canned_text="ok")), governance=hook)
    result = orchestrator.run("hello")
    assert hook.before_calls == 1
    assert hook.after_calls == 1
    assert result.text == "[reviewed] ok"


def test_governance_hook_can_block():
    hook = _BlockingGovernanceHook()
    orchestrator = Orchestrator(model=_catalog_entry(EchoProvider(canned_text="ok")), governance=hook)
    with pytest.raises(PermissionError):
        orchestrator.run("this is forbidden content")
