"""The orchestrator — the tool-calling agent loop.

Dispatch a prompt to a model, execute any tools it asks for, feed results
back, repeat until the model returns a final answer or the iteration cap is
hit. This is the generic, model-agnostic dispatch pattern; it has no opinion
about identity, policy, or audit — those are the GovernanceHook's job.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .catalog import ModelEntry
from .governance import GovernanceHook, NoOpGovernanceHook
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
    ) -> OrchestratorResult:
        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        tool_schemas = self.tools.schemas() if len(self.tools) else None
        tool_calls_made: list[ToolCall] = []

        for iteration in range(1, max_tool_iterations + 1):
            gated_messages = self.governance.before_dispatch(messages)
            response = self.model.provider.complete(gated_messages, tools=tool_schemas)

            if response.tool_calls:
                messages.append({
                    "role": "assistant",
                    "content": response.text,
                    "tool_calls": [tc.__dict__ for tc in response.tool_calls],
                })
                for call in response.tool_calls:
                    tool_calls_made.append(call)
                    result = self.tools.execute(call.name, call.arguments)
                    messages.append({"role": "tool", "tool_call_id": call.id, "content": str(result)})
                continue

            final_text = self.governance.after_dispatch(messages, response.text)
            return OrchestratorResult(
                text=final_text or "",
                messages=messages,
                tool_calls_made=tool_calls_made,
                iterations=iteration,
            )

        raise MaxIterationsExceeded(
            f"no final answer after {max_tool_iterations} tool-calling iterations"
        )
