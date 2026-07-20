"""The governance extension point.

This is the seam where a real deployment plugs in policy: identity/authority
checks, prompt-policy enforcement, audit-trail capture, cost/rate limiting,
anything that has to run before a request reaches a model, before a tool
executes, or before a response reaches a caller. The open core ships only
the interface and a no-op default — the actual policy engine (the "harness"
in the sense of the public AI Harness Engineering Standard, github.com/
ologos-repos/ai-harness-engineering) is what Ologos operates as a governed
product on top of this core. See ologos.co/aioc for the managed/governed
version.

Implement your own by subclassing GovernanceHook.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .context import ExecutionContext
from .decisions import DecisionDisposition, GovernanceDecision


class GovernanceBlocked(Exception):
    """Base class: a governance decision prevented an action from running."""

    def __init__(self, decision: GovernanceDecision):
        self.decision = decision
        detail = f" — {decision.message}" if decision.message else ""
        super().__init__(f"{decision.disposition.value}: {decision.reason_code}{detail}")


class ActionDenied(GovernanceBlocked):
    """Raised when a tool call's governance decision is DENY."""


class ConfirmationRequired(GovernanceBlocked):
    """Raised when a tool call's governance decision is REQUIRE_CONFIRMATION.
    A governed deployment would surface this to a human and re-invoke on
    approval; this open core doesn't implement that flow, only the gate."""


class GovernanceHook(ABC):
    @abstractmethod
    def before_dispatch(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Called with the outbound message list before it reaches a provider.
        Return the (possibly modified) messages, or raise to block the call."""
        raise NotImplementedError

    @abstractmethod
    def after_dispatch(self, messages: list[dict[str, Any]], response_text: str | None) -> str | None:
        """Called with the final response text before it's returned to the
        caller. Return the (possibly modified) text, or raise to block it."""
        raise NotImplementedError

    def evaluate_tool_call(
        self,
        context: ExecutionContext | None,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> GovernanceDecision:
        """Called before a tool's handler executes. Default: always ALLOW.

        Override to apply real policy. A DENY or REQUIRE_CONFIRMATION
        disposition prevents the tool's handler from being invoked at all —
        this is the mechanism, not just an event fired after the fact."""
        return GovernanceDecision.allow()


class NoOpGovernanceHook(GovernanceHook):
    """Pass-through default — does nothing. This is what ships in the open
    core; a governed deployment supplies a real implementation."""

    def before_dispatch(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return messages

    def after_dispatch(self, messages: list[dict[str, Any]], response_text: str | None) -> str | None:
        return response_text
