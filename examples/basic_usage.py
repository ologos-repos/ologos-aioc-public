"""Runnable, dependency-free demo: no API key needed (uses EchoProvider).

    python3 examples/basic_usage.py

Swap EchoProvider for OpenAICompatibleProvider("gpt-4o-mini") — or any other
ModelProvider subclass — to use a real backend; nothing else in this file
changes.
"""
from ologos_aioc import EchoProvider, ModelCatalog, Orchestrator, Tool, ToolRegistry


def get_weather(city: str = "Fayetteville") -> str:
    return f"It's 72F and sunny in {city}."


def main() -> None:
    catalog = ModelCatalog()
    catalog.register("demo-model", EchoProvider(), tags={"fast"})

    tools = ToolRegistry()
    tools.register(Tool(
        name="weather",
        description="Get the current weather for a city",
        parameters={"type": "object", "properties": {"city": {"type": "string"}}},
        handler=get_weather,
    ))

    orchestrator = Orchestrator(model=catalog.route("fast"), tools=tools)
    result = orchestrator.run("please call weather for me")

    print(f"Final answer:  {result.text}")
    print(f"Tool calls:    {[c.name for c in result.tool_calls_made]}")
    print(f"Iterations:    {result.iterations}")


if __name__ == "__main__":
    main()
