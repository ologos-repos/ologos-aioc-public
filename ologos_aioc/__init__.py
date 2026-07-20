"""ologos_aioc — a small, model-agnostic orchestration core.

Public API:
    ModelProvider, ModelResponse, EchoProvider, OpenAICompatibleProvider
    ModelCatalog, ModelEntry
    Tool, ToolRegistry
    GovernanceHook, NoOpGovernanceHook
    Orchestrator, OrchestratorResult
"""

from .providers import EchoProvider, ModelProvider, ModelResponse, OpenAICompatibleProvider
from .catalog import ModelCatalog, ModelEntry
from .tools import Tool, ToolRegistry
from .governance import GovernanceHook, NoOpGovernanceHook
from .orchestrator import Orchestrator, OrchestratorResult

__version__ = "0.1.0"

__all__ = [
    "ModelProvider",
    "ModelResponse",
    "EchoProvider",
    "OpenAICompatibleProvider",
    "ModelCatalog",
    "ModelEntry",
    "Tool",
    "ToolRegistry",
    "GovernanceHook",
    "NoOpGovernanceHook",
    "Orchestrator",
    "OrchestratorResult",
    "__version__",
]
