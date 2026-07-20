"""The operational lifecycle — the stages a governed run passes through.

This is the core architectural claim of this library: governance isn't
"intercept the prompt and intercept the response." It's a lifecycle with
named stages, each of which is a point where a decision or an evidence
record can attach. What a governed deployment *does* at each stage is
proprietary; that a stage exists, and that every run passes through the
same named sequence, is the public contract.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Mapping


class OperationStage(Enum):
    REQUEST_RECEIVED = "request_received"
    MODEL_SELECTED = "model_selected"
    MODEL_DISPATCH = "model_dispatch"
    MODEL_RESPONSE = "model_response"
    TOOL_REQUEST = "tool_request"
    TOOL_RESULT = "tool_result"
    RESPONSE_RELEASE = "response_release"
    RUN_COMPLETED = "run_completed"
    RUN_FAILED = "run_failed"


@dataclass(frozen=True)
class EvidenceEvent:
    event_id: str
    run_id: str
    stage: OperationStage
    occurred_at: datetime
    subject: str
    outcome: str
    attributes: Mapping[str, Any] = field(default_factory=dict)
