import json

from ologos_aioc import InMemoryEvidenceRecorder, JsonLinesEvidenceRecorder, OperationStage


def test_in_memory_recorder():
    rec = InMemoryEvidenceRecorder()
    event = rec.record("run-1", OperationStage.REQUEST_RECEIVED, "orchestrator", "received", {"k": "v"})
    assert len(rec.events) == 1
    assert rec.events[0] is event
    assert event.run_id == "run-1"
    assert event.stage is OperationStage.REQUEST_RECEIVED
    assert event.attributes == {"k": "v"}
    assert event.event_id


def test_jsonlines_recorder_writes_valid_json(tmp_path):
    path = tmp_path / "evidence.jsonl"
    rec = JsonLinesEvidenceRecorder(path)
    rec.record("run-1", OperationStage.RUN_COMPLETED, "orchestrator", "completed", {"iterations": 2})
    rec.record("run-1", OperationStage.RUN_FAILED, "orchestrator", "failed")

    lines = path.read_text().strip().splitlines()
    assert len(lines) == 2
    row = json.loads(lines[0])
    assert row["run_id"] == "run-1"
    assert row["stage"] == "run_completed"
    assert row["outcome"] == "completed"
    assert row["attributes"] == {"iterations": 2}
    assert "occurred_at" in row and "event_id" in row
