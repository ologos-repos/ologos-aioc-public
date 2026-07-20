"""Execution context — the identity of a single governed run.

Every call into the orchestrator happens on behalf of someone, for some
purpose, in some domain. ExecutionContext carries that generic operational
metadata through the run so a governance layer has something to reason
about. It intentionally carries no opinion about what an "actor" or
"domain" *means* in your deployment — that's what a governed identity/
authority system supplies, not this open core.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class ExecutionContext:
    run_id: str
    actor_id: str | None = None
    session_id: str | None = None
    purpose: str | None = None
    domain: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @staticmethod
    def new(
        actor_id: str | None = None,
        session_id: str | None = None,
        purpose: str | None = None,
        domain: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> "ExecutionContext":
        """Convenience constructor: generates a fresh run_id."""
        return ExecutionContext(
            run_id=str(uuid.uuid4()),
            actor_id=actor_id,
            session_id=session_id,
            purpose=purpose,
            domain=domain,
            metadata=metadata or {},
        )
