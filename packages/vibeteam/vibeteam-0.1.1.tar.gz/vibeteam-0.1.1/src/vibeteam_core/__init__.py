"""
Vibeteam Core - Universal MCP Agent Orchestration Framework

A framework for building intelligent agent orchestrators that work across
different coding tools and environments.
"""

from .adapters import ToolAdapter, ToolCapability
from .agents import AgentCapability, AgentMetadata, AgentRegistry, AgentResult, BaseAgent
from .orchestrator import CoreOrchestrator, OrchestratorConfig

__version__ = "0.1.0"
__all__ = [
    "BaseAgent",
    "AgentCapability",
    "AgentResult",
    "CoreOrchestrator",
    "OrchestratorConfig",
    "AgentRegistry",
    "AgentMetadata",
    "ToolAdapter",
    "ToolCapability",
]
