"""Evidence recording — proof that a governed run actually happened.

An AI Operations Center doesn't just execute work; it produces evidence
that governed work occurred. These recorders are deliberately minimal and
explicitly NOT tamper-evident, signed, access-controlled, or suitable for
production audit — they exist to demonstrate the shape of the contract
(every stage transition can produce a record), not to be an audit system.
A governed deployment's real evidence plane — chaining, signing, storage,
redaction, retention — is not part of this open core.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Protocol

from .events import EvidenceEvent, OperationStage


class EvidenceRecorder(Protocol):
    def record(
        self,
        run_id: str,
        stage: OperationStage,
        subject: str,
        outcome: str,
        attributes: Mapping[str, Any] | None = None,
    ) -> EvidenceEvent: ...


def _new_event(run_id, stage, subject, outcome, attributes) -> EvidenceEvent:
    return EvidenceEvent(
        event_id=str(uuid.uuid4()),
        run_id=run_id,
        stage=stage,
        occurred_at=datetime.now(timezone.utc),
        subject=subject,
        outcome=outcome,
        attributes=attributes or {},
    )


class InMemoryEvidenceRecorder:
    """Illustrative only. Holds events in a plain list for the lifetime of
    the process — no persistence, no tamper-evidence."""

    def __init__(self) -> None:
        self.events: list[EvidenceEvent] = []

    def record(self, run_id, stage, subject, outcome, attributes=None) -> EvidenceEvent:
        event = _new_event(run_id, stage, subject, outcome, attributes)
        self.events.append(event)
        return event


class JsonLinesEvidenceRecorder:
    """Illustrative only. Appends one JSON object per event to a local
    file. No signing, no chaining, no access control, no retention policy —
    a governed deployment's real evidence plane replaces this entirely."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def record(self, run_id, stage, subject, outcome, attributes=None) -> EvidenceEvent:
        event = _new_event(run_id, stage, subject, outcome, attributes)
        row = {
            "event_id": event.event_id,
            "run_id": event.run_id,
            "stage": event.stage.value,
            "occurred_at": event.occurred_at.isoformat(),
            "subject": event.subject,
            "outcome": event.outcome,
            "attributes": dict(event.attributes),
        }
        with self.path.open("a") as f:
            f.write(json.dumps(row) + "\n")
        return event
