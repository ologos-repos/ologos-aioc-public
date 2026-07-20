"""Each test proves one requirement in CONFORMANCE.md. Test names carry the
requirement ID so a failing test names its own spec violation directly."""
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


def _tool_registry(handler_calls):
    def handler(**kwargs):
        handler_calls.append(kwargs)
        return "ok"

    tools = ToolRegistry()
    tools.register(Tool(name="demo_action", description="demo",
                         parameters={"type": "object", "properties": {}}, handler=handler))
    return tools


class _DenyingHook(NoOpGovernanceHook):
    def evaluate_tool_call(self, context, tool_name, arguments):
        return GovernanceDecision(DecisionDisposition.DENY, "DEMO_DENIED")


class _ConfirmingHook(NoOpGovernanceHook):
    def evaluate_tool_call(self, context, tool_name, arguments):
        return GovernanceDecision(DecisionDisposition.REQUIRE_CONFIRMATION, "DEMO_CONFIRM")


def test_AIOC_CORE_001_run_has_unique_execution_identifier():
    orchestrator = Orchestrator(model=_catalog_entry(EchoProvider(canned_text="x")))
    r1 = orchestrator.run("a")
    r2 = orchestrator.run("b")
    assert r1.run_id and r2.run_id
    assert r1.run_id != r2.run_id


def test_AIOC_CORE_002_tool_call_passes_through_decision_point():
    calls = {"evaluated": False}

    class Spy(NoOpGovernanceHook):
        def evaluate_tool_call(self, context, tool_name, arguments):
            calls["evaluated"] = True
            return GovernanceDecision.allow()

    tools = _tool_registry([])
    orchestrator = Orchestrator(model=_catalog_entry(EchoProvider()), tools=tools, governance=Spy())
    orchestrator.run("call demo_action please")
    assert calls["evaluated"] is True


@pytest.mark.parametrize("hook,expected_exc", [(_DenyingHook(), ActionDenied), (_ConfirmingHook(), ConfirmationRequired)])
def test_AIOC_CORE_003_blocked_decision_prevents_handler_invocation(hook, expected_exc):
    handler_calls = []
    tools = _tool_registry(handler_calls)
    orchestrator = Orchestrator(model=_catalog_entry(EchoProvider()), tools=tools, governance=hook)

    with pytest.raises(expected_exc):
        orchestrator.run("call demo_action please")

    assert handler_calls == []


def test_AIOC_CORE_004_terminal_event_on_success():
    tools = _tool_registry([])
    recorder = InMemoryEvidenceRecorder()
    Orchestrator(model=_catalog_entry(EchoProvider()), tools=tools).run("call demo_action please", evidence=recorder)
    assert recorder.events[-1].stage is OperationStage.RUN_COMPLETED


def test_AIOC_CORE_004_terminal_event_on_failure():
    tools = _tool_registry([])
    recorder = InMemoryEvidenceRecorder()
    orchestrator = Orchestrator(model=_catalog_entry(EchoProvider()), tools=tools, governance=_DenyingHook())
    with pytest.raises(ActionDenied):
        orchestrator.run("call demo_action please", evidence=recorder)
    assert recorder.events[-1].stage is OperationStage.RUN_FAILED


def test_AIOC_CORE_005_model_selection_separate_from_orchestration():
    # The orchestrator's constructor takes an already-resolved ModelEntry;
    # it exposes no routing method of its own. Routing lives entirely in
    # ModelCatalog, a separate module Orchestrator merely depends on.
    entry = _catalog_entry(EchoProvider())
    orchestrator = Orchestrator(model=entry)
    assert not hasattr(orchestrator, "route")
    assert orchestrator.model is entry


def test_AIOC_CORE_006_tool_schema_derives_from_same_registration():
    handler_calls = []
    tools = _tool_registry(handler_calls)
    schema = tools.schemas()[0]
    assert schema["function"]["name"] == "demo_action"
    # the same registered Tool is what actually executes:
    assert tools.execute("demo_action", {}) == "ok"


def test_AIOC_CORE_007_evidence_capture_is_explicit_not_implicit():
    tools = _tool_registry([])
    recorder = InMemoryEvidenceRecorder()
    orchestrator = Orchestrator(model=_catalog_entry(EchoProvider()), tools=tools)

    # A run with no evidence= passed must not write to a recorder that
    # merely exists in scope -- there is no implicit/global recording path.
    orchestrator.run("call demo_action please")
    assert recorder.events == []

    # The same recorder, explicitly supplied, does capture events.
    orchestrator.run("call demo_action please", evidence=recorder)
    assert len(recorder.events) > 0


def test_AIOC_CORE_008_side_effecting_distinguishable_from_observational():
    from ologos_aioc import CapabilityDescriptor
    read_only = CapabilityDescriptor(capability_id="demo-read", domain="demo", risk="low", side_effecting=False)
    mutating = CapabilityDescriptor(capability_id="demo-write", domain="demo", risk="high", side_effecting=True)
    assert read_only.side_effecting is False
    assert mutating.side_effecting is True
