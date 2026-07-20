"""Model provider abstraction.

A ModelProvider is anything that can turn a list of chat messages (plus an
optional tool schema) into a ModelResponse. The orchestrator never talks to
a specific vendor SDK directly — only to this interface — so swapping or
mixing providers never touches orchestration logic.
"""
from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    """A single tool invocation the model asked for."""
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class ModelResponse:
    """Normalized response shape every provider returns, regardless of vendor."""
    text: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    raw: Any = None  # the untouched vendor response, for debugging/logging


class ModelProvider(ABC):
    """Base class every provider implements. Subclass this to add a new backend."""

    @abstractmethod
    def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> ModelResponse:
        """Send `messages` (OpenAI chat-message-shape dicts) and an optional
        list of tool schemas (OpenAI tool-schema shape). Return a ModelResponse."""
        raise NotImplementedError


class EchoProvider(ModelProvider):
    """A deterministic, network-free provider for tests, demos, and CI.

    Useful on its own to exercise the orchestrator's tool-calling loop without
    an API key: if the last user message matches a registered tool's name
    (case-insensitively, e.g. "call weather"), it emits a tool call for it
    once, then echoes the tool's result back as the final answer.
    """

    def __init__(self, canned_text: str | None = None) -> None:
        self.canned_text = canned_text
        self._call_count = 0

    def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> ModelResponse:
        self._call_count += 1
        last_user = next((m for m in reversed(messages) if m.get("role") == "user"), None)
        last_tool_result = next((m for m in reversed(messages) if m.get("role") == "tool"), None)

        if last_tool_result is not None:
            return ModelResponse(text=f"Final answer, using tool result: {last_tool_result['content']}")

        if tools and last_user:
            for tool_schema in tools:
                name = tool_schema["function"]["name"]
                if name.lower() in last_user.get("content", "").lower():
                    return ModelResponse(
                        tool_calls=[ToolCall(id=f"call_{self._call_count}", name=name, arguments={})]
                    )

        if self.canned_text is not None:
            return ModelResponse(text=self.canned_text)
        return ModelResponse(text="(echo) " + (last_user.get("content", "") if last_user else ""))


class OpenAICompatibleProvider(ModelProvider):
    """Talks to any OpenAI-chat-completions-compatible endpoint (OpenAI itself,
    and most self-hosted / open-weight serving stacks that mirror that API).

    Requires the `openai` package (an optional dependency — see extras in
    pyproject.toml) and either an explicit api_key/base_url or the standard
    OPENAI_API_KEY / OPENAI_BASE_URL environment variables.
    """

    def __init__(
        self,
        model: str,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        try:
            import openai
        except ImportError as exc:
            raise ImportError(
                "OpenAICompatibleProvider requires the 'openai' package: "
                "pip install 'ologos-aioc[openai]'"
            ) from exc
        self.model = model
        self._client = openai.OpenAI(
            api_key=api_key or os.environ.get("OPENAI_API_KEY"),
            base_url=base_url or os.environ.get("OPENAI_BASE_URL"),
        )

    def complete(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> ModelResponse:
        kwargs: dict[str, Any] = {"model": self.model, "messages": messages}
        if tools:
            kwargs["tools"] = tools
        response = self._client.chat.completions.create(**kwargs)
        choice = response.choices[0].message
        tool_calls = [
            ToolCall(id=tc.id, name=tc.function.name, arguments=json.loads(tc.function.arguments or "{}"))
            for tc in (choice.tool_calls or [])
        ]
        return ModelResponse(text=choice.content, tool_calls=tool_calls, raw=response)
