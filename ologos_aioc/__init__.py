"""ologos_aioc — a reference architecture and executable kernel for the
control plane beneath an AI Operations Center (AIOC).

Public API:
    ModelProvider, ModelResponse, EchoProvider, OpenAICompatibleProvider
    ModelCatalog, ModelEntry
    Tool, ToolRegistry
    CapabilityDescriptor
    ExecutionContext
    OperationStage, EvidenceEvent
    DecisionDisposition, GovernanceDecision
    GovernanceHook, NoOpGovernanceHook, GovernanceBlocked, ActionDenied, ConfirmationRequired
    EvidenceRecorder, InMemoryEvidenceRecorder, JsonLinesEvidenceRecorder
    Orchestrator, OrchestratorResult, MaxIterationsExceeded
"""

from .providers import EchoProvider, ModelProvider, ModelResponse, OpenAICompatibleProvider
from .capabilities import CapabilityDescriptor
from .catalog import ModelCatalog, ModelEntry
from .context import ExecutionContext
from .decisions import DecisionDisposition, GovernanceDecision
from .events import EvidenceEvent, OperationStage
from .evidence import EvidenceRecorder, InMemoryEvidenceRecorder, JsonLinesEvidenceRecorder
from .profiles import DomainCapability, DomainProfile, load_profile
from .tools import Tool, ToolRegistry
from .governance import (
    ActionDenied,
    ConfirmationRequired,
    GovernanceBlocked,
    GovernanceHook,
    NoOpGovernanceHook,
)
from .orchestrator import MaxIterationsExceeded, Orchestrator, OrchestratorResult

__version__ = "0.2.0"

__all__ = [
    "ModelProvider",
    "ModelResponse",
    "EchoProvider",
    "OpenAICompatibleProvider",
    "ModelCatalog",
    "ModelEntry",
    "Tool",
    "ToolRegistry",
    "CapabilityDescriptor",
    "ExecutionContext",
    "OperationStage",
    "EvidenceEvent",
    "DecisionDisposition",
    "GovernanceDecision",
    "GovernanceHook",
    "NoOpGovernanceHook",
    "GovernanceBlocked",
    "ActionDenied",
    "ConfirmationRequired",
    "EvidenceRecorder",
    "InMemoryEvidenceRecorder",
    "JsonLinesEvidenceRecorder",
    "DomainCapability",
    "DomainProfile",
    "load_profile",
    "Orchestrator",
    "OrchestratorResult",
    "MaxIterationsExceeded",
    "__version__",
]
