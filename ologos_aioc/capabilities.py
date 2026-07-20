"""Capability metadata — models and tools as governed resources, not bare
functions.

Attaching a CapabilityDescriptor to a model or a tool is what lets routing
and governance reason about risk and side effects instead of treating
every callable identically. The actual risk taxonomy, domain inventory,
and routing policy a real deployment uses are proprietary; the shape of
"a capability has a domain, a risk tier, and a side-effect flag" is the
public contract.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CapabilityDescriptor:
    capability_id: str
    domain: str
    risk: str
    side_effecting: bool
    confirmation_recommended: bool = False
    tags: frozenset[str] = field(default_factory=frozenset)
