"""
Agent abstractions and base classes for the Vibeteam framework.
"""

from .base import AgentCapability, AgentResult, AgentType, BaseAgent
from .registry import AgentMetadata, AgentRegistry, get_global_registry

__all__ = [
    "BaseAgent",
    "AgentCapability",
    "AgentResult",
    "AgentType",
    "AgentRegistry",
    "AgentMetadata",
    "get_global_registry",
]
