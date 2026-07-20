"""Model catalog — a small, named registry of providers with capability tags,
so calling code asks for what it needs ("cheap", "reasoning", "vision")
rather than hardcoding a specific vendor/model string.

This is deliberately simple: a governed enterprise deployment (identity-
bound dispatch gating, per-tenant policy, cost ceilings, audit trail on
every route decision) is Ologos's commercial product built on top of this
interface, not part of the open core. See ologos.co/aioc.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .providers import ModelProvider


@dataclass
class ModelEntry:
    name: str
    provider: ModelProvider
    tags: set[str] = field(default_factory=set)


class ModelCatalog:
    """Register named models, then route by name or by required tag."""

    def __init__(self) -> None:
        self._entries: dict[str, ModelEntry] = {}

    def register(self, name: str, provider: ModelProvider, tags: set[str] | None = None) -> None:
        self._entries[name] = ModelEntry(name=name, provider=provider, tags=tags or set())

    def get(self, name: str) -> ModelEntry:
        try:
            return self._entries[name]
        except KeyError as exc:
            raise KeyError(f"no model registered under name {name!r}; known: {list(self._entries)}") from exc

    def route(self, required_tag: str) -> ModelEntry:
        """Return the first registered entry carrying `required_tag`.

        Deliberately simple (first match, registration order) — a real
        deployment would weigh cost/latency/availability/policy here; that's
        the enterprise dispatch-gate layer, not this open core's job.
        """
        for entry in self._entries.values():
            if required_tag in entry.tags:
                return entry
        raise LookupError(f"no registered model carries tag {required_tag!r}; known: {list(self._entries)}")

    def __contains__(self, name: str) -> bool:
        return name in self._entries

    def __len__(self) -> int:
        return len(self._entries)
