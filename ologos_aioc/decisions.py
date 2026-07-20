"""Governance decisions — the mechanistic output of a policy evaluation.

A governance layer that can't be reduced to "what do I do with this
request" isn't operationally enforceable. This module defines the shape
every governance decision takes; it defines no policy content. The real
question — which disposition a given actor/action/domain combination
deserves — is exactly the proprietary part a governed deployment supplies.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DecisionDisposition(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_CONFIRMATION = "require_confirmation"
    MODIFY = "modify"


@dataclass(frozen=True)
class GovernanceDecision:
    disposition: DecisionDisposition
    reason_code: str
    message: str | None = None
    obligations: tuple[str, ...] = ()

    @staticmethod
    def allow(reason_code: str = "DEMO_ALLOWED", message: str | None = None) -> "GovernanceDecision":
        return GovernanceDecision(DecisionDisposition.ALLOW, reason_code, message)
