import pytest

from ologos_aioc import (
    ActionDenied,
    ConfirmationRequired,
    DecisionDisposition,
    EchoProvider,
    GovernanceDecision,
    InMemoryEvidenceRecorder,
    ModelCatalog,
    NoOpGovernanceHook,
    OperationStage,
    Orchestrator,
    Tool,
    ToolRegistry,
)


def _catalog_entry(provider):
    catalog = ModelCatalog()
    catalog.register("m", provider)
    return catalog.get("m")


def _tool_registry(calls):
    def handler(**kwargs):
        calls.append(kwargs)
        return "72F and sunny"

    tools = ToolRegistry()
    tools.register(Tool(name="weather", description="Get the weather",
                         parameters={"type": "object", "properties": {}}, handler=handler))
    return tools


class _DenyingHook(NoOpGovernanceHook):
    def evaluate_tool_call(self, context, tool_name, arguments):
        return GovernanceDecision(DecisionDisposition.DENY, "DEMO_DENIED", "blocked for test")


class _ConfirmingHook(NoOpGovernanceHook):
    def evaluate_tool_call(self, context, tool_name, arguments):
        return GovernanceDecision(DecisionDisposition.REQUIRE_CONFIRMATION, "DEMO_NEEDS_CONFIRMATION")


def test_denied_tool_call_never_invokes_handler():
    calls = []
    tools = _tool_registry(calls)
    orchestrator = Orchestrator(model=_catalog_entry(EchoProvider()), tools=tools, governance=_DenyingHook())

    with pytest.raises(ActionDenied):
        orchestrator.run("call weather please")

    assert calls == []  # the handler must never run


def test_confirmation_required_never_invokes_handler():
    calls = []
    tools = _tool_registry(calls)
    orchestrator = Orchestrator(model=_catalog_entry(EchoProvider()), tools=tools, governance=_ConfirmingHook())

    with pytest.raises(ConfirmationRequired):
        orchestrator.run("call weather please")

    assert calls == []


def test_default_governance_allows_tool_call():
    calls = []
    tools = _tool_registry(calls)
    orchestrator = Orchestrator(model=_catalog_entry(EchoProvider()), tools=tools)
    result = orchestrator.run("call weather please")
    assert len(calls) == 1
    assert "72F and sunny" in result.text


def test_evidence_records_full_lifecycle_on_success():
    tools = _tool_registry([])
    recorder = InMemoryEvidenceRecorder()
    orchestrator = Orchestrator(model=_catalog_entry(EchoProvider()), tools=tools)
    result = orchestrator.run("call weather please", evidence=recorder)

    stages = [e.stage for e in recorder.events]
    assert stages[0] is OperationStage.REQUEST_RECEIVED
    assert OperationStage.MODEL_SELECTED in stages
    assert OperationStage.TOOL_REQUEST in stages
    assert OperationStage.TOOL_RESULT in stages
    assert stages[-1] is OperationStage.RUN_COMPLETED
    assert all(e.run_id == result.run_id for e in recorder.events)


def test_evidence_records_run_failed_on_denial():
    tools = _tool_registry([])
    recorder = InMemoryEvidenceRecorder()
    orchestrator = Orchestrator(model=_catalog_entry(EchoProvider()), tools=tools, governance=_DenyingHook())

    with pytest.raises(ActionDenied):
        orchestrator.run("call weather please", evidence=recorder)

    stages = [e.stage for e in recorder.events]
    assert OperationStage.RUN_FAILED in stages
    assert OperationStage.RUN_COMPLETED not in stages


def test_result_carries_run_id():
    orchestrator = Orchestrator(model=_catalog_entry(EchoProvider(canned_text="hi")))
    result = orchestrator.run("hello")
    assert result.run_id
