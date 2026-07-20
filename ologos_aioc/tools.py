"""Tool definitions and a registry the orchestrator can execute against."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .capabilities import CapabilityDescriptor


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema for the tool's arguments
    handler: Callable[..., Any]
    capability: CapabilityDescriptor | None = None

    def to_schema(self) -> dict[str, Any]:
        """OpenAI tool-schema shape — the format most providers expect."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"no tool registered under name {name!r}; known: {list(self._tools)}") from exc

    def schemas(self) -> list[dict[str, Any]]:
        return [t.to_schema() for t in self._tools.values()]

    def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        return self.get(name).handler(**arguments)

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools
