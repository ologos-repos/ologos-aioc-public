"""Demonstrates the evidence plane: every lifecycle stage of a run produces
a record.

    python3 examples/evidence_capture.py

Writes to ./demo-evidence.jsonl and prints what was captured. This
recorder is illustrative only -- not tamper-evident, not signed, not
suitable for production audit. See ologos_aioc/evidence.py.
"""
import json
from pathlib import Path

from ologos_aioc import EchoProvider, JsonLinesEvidenceRecorder, ModelCatalog, Orchestrator, Tool, ToolRegistry


def get_weather(city: str = "Fayetteville") -> str:
    return f"It's 72F and sunny in {city}."


def main() -> None:
    catalog = ModelCatalog()
    catalog.register("demo-model", EchoProvider(), tags={"fast"})

    tools = ToolRegistry()
    tools.register(Tool(
        name="weather", description="Get the weather for a city",
        parameters={"type": "object", "properties": {"city": {"type": "string"}}},
        handler=get_weather,
    ))

    path = Path("demo-evidence.jsonl")
    path.unlink(missing_ok=True)
    recorder = JsonLinesEvidenceRecorder(path)

    orchestrator = Orchestrator(model=catalog.route("fast"), tools=tools)
    result = orchestrator.run("please call weather for me", evidence=recorder)

    print(f"Run {result.run_id} completed: {result.text}\n")
    print(f"Evidence written to {path}:")
    for line in path.read_text().splitlines():
        row = json.loads(line)
        print(f"  [{row['stage']:>18}] {row['subject']:<20} -> {row['outcome']}")


if __name__ == "__main__":
    main()
