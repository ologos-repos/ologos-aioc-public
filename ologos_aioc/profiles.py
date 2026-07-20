"""Domain-console profiles — declarative capability surfaces per operating
domain.

A governed AIOC deployment composes role- and domain-oriented consoles
over the same control plane; which capabilities a given domain can see and
invoke is data, not code. This loader reads that declarative shape. The
real console implementation, navigation, and enterprise domain inventory
are not part of this open core -- see profiles/*.yaml for illustrative
examples only.

Requires PyYAML (optional extra: pip install 'ologos-aioc[profiles]').
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DomainCapability:
    id: str
    risk: str
    side_effecting: bool
    confirmation_recommended: bool = False


@dataclass(frozen=True)
class DomainProfile:
    id: str
    level: str
    title: str
    description: str
    capabilities: tuple[DomainCapability, ...] = field(default_factory=tuple)
    views: tuple[str, ...] = field(default_factory=tuple)


def load_profile(path: str | Path) -> DomainProfile:
    try:
        import yaml
    except ImportError as exc:
        raise ImportError(
            "load_profile requires PyYAML: pip install 'ologos-aioc[profiles]'"
        ) from exc

    raw: dict[str, Any] = yaml.safe_load(Path(path).read_text())
    capabilities = tuple(
        DomainCapability(
            id=c["id"],
            risk=c["risk"],
            side_effecting=c["side_effecting"],
            confirmation_recommended=c.get("confirmation_recommended", False),
        )
        for c in raw.get("capabilities", [])
    )
    return DomainProfile(
        id=raw["id"],
        level=raw["level"],
        title=raw["title"],
        description=raw.get("description", "").strip(),
        capabilities=capabilities,
        views=tuple(raw.get("views", [])),
    )
