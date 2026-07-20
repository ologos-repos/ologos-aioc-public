"""The orchestrator — the tool-calling agent loop.

Dispatch a prompt to a model, execute any tools it asks for, feed results
back, repeat until the model returns a final answer or the iteration cap is
hit. This is the generic, model-agnostic dispatch pattern; it has no opinion
about identity, policy, or audit content — those are the GovernanceHook's
job. What this module *does* own: every run gets an ExecutionContext, every
tool call passes through a governance decision point before its handler
runs, and (if an EvidenceRecorder is supplied) every stage of the lifecycle
produces a record.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .catalog import ModelEntry
from .context import ExecutionContext
from .decisions import DecisionDisposition
from .events import OperationStage
from .evidence import EvidenceRecorder
from .governance import ActionDenied, ConfirmationRequired, GovernanceHook, NoOpGovernanceHook
from .providers import ToolCall
from .tools import ToolRegistry


class MaxIterationsExceeded(RuntimeError):
    """Raised when the tool-calling loop hits max_tool_iterations without a
    final answer — a runaway-loop backstop, not an expected outcome."""


@dataclass
class OrchestratorResult:
    text: str
    messages: list[dict[str, Any]]
    tool_calls_made: list[ToolCall] = field(default_factory=list)
    iterations: int = 0
    run_id: str = ""


class Orchestrator:
    def __init__(
        self,
        model: ModelEntry,
        tools: ToolRegistry | None = None,
        governance: GovernanceHook | None = None,
    ) -> None:
        self.model = model
        self.tools = tools or ToolRegistry()
        self.governance = governance or NoOpGovernanceHook()

    def run(
        self,
        prompt: str,
        system: str | None = None,
        max_tool_iterations: int = 5,
        context: ExecutionContext | None = None,
        evidence: EvidenceRecorder | None = None,
    ) -> OrchestratorResult:
        context = context or ExecutionContext.new()

        def record(stage: OperationStage, subject: str, outcome: str, **attributes: Any) -> None:
            if evidence is not None:
                evidence.record(context.run_id, stage, subject, outcome, attributes)

        record(OperationStage.REQUEST_RECEIVED, "orchestrator", "received", prompt_length=len(prompt))
        record(OperationStage.MODEL_SELECTED, self.model.name, "selected")

        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        tool_schemas = self.tools.schemas() if len(self.tools) else None
        tool_calls_made: list[ToolCall] = []

        try:
            for iteration in range(1, max_tool_iterations + 1):
                gated_messages = self.governance.before_dispatch(messages)
                record(OperationStage.MODEL_DISPATCH, self.model.name, "dispatched", iteration=iteration)
                response = self.model.provider.complete(gated_messages, tools=tool_schemas)
                record(OperationStage.MODEL_RESPONSE, self.model.name, "responded",
                       tool_calls=len(response.tool_calls))

                if response.tool_calls:
                    messages.append({
                        "role": "assistant",
                        "content": response.text,
                        "tool_calls": [tc.__dict__ for tc in response.tool_calls],
                    })
                    for call in response.tool_calls:
                        tool_calls_made.append(call)
                        record(OperationStage.TOOL_REQUEST, call.name, "requested")

                        decision = self.governance.evaluate_tool_call(context, call.name, call.arguments)
                        if decision.disposition is DecisionDisposition.DENY:
                            record(OperationStage.TOOL_RESULT, call.name, "denied", reason_code=decision.reason_code)
                            raise ActionDenied(decision)
                        if decision.disposition is DecisionDisposition.REQUIRE_CONFIRMATION:
                            record(OperationStage.TOOL_RESULT, call.name, "confirmation_required",
                                   reason_code=decision.reason_code)
                            raise ConfirmationRequired(decision)

                        result = self.tools.execute(call.name, call.arguments)
                        record(OperationStage.TOOL_RESULT, call.name, "executed")
                        messages.append({"role": "tool", "tool_call_id": call.id, "content": str(result)})
                    continue

                final_text = self.governance.after_dispatch(messages, response.text)
                record(OperationStage.RESPONSE_RELEASE, "orchestrator", "released")
                record(OperationStage.RUN_COMPLETED, "orchestrator", "completed", iterations=iteration)
                return OrchestratorResult(
                    text=final_text or "",
                    messages=messages,
                    tool_calls_made=tool_calls_made,
                    iterations=iteration,
                    run_id=context.run_id,
                )

            raise MaxIterationsExceeded(
                f"no final answer after {max_tool_iterations} tool-calling iterations"
            )
        except Exception as caught:
            record(OperationStage.RUN_FAILED, "orchestrator", "failed", reason=type(caught).__name__)
            raise
