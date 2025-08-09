"""
Agent registry for discovering and managing available agents.
"""

from typing import Dict, List, Optional, Type

from pydantic import BaseModel, Field

from .base import AgentCapability, AgentType, BaseAgent


class AgentMetadata(BaseModel):
    """Metadata about a registered agent."""

    name: str
    agent_type: AgentType
    version: str
    description: str
    capabilities: List[AgentCapability]
    supported_tools: List[str] = Field(default_factory=list)
    author: Optional[str] = None
    package_name: Optional[str] = None
    entry_point: Optional[str] = None
    quality_score: float = Field(ge=0.0, le=10.0, default=5.0)
    usage_count: int = Field(ge=0, default=0)


class AgentRegistry:
    """Registry for discovering and managing available agents."""

    def __init__(self):
        self._agents: Dict[str, Type[BaseAgent]] = {}
        self._metadata: Dict[str, AgentMetadata] = {}

    def register(self, agent_class: Type[BaseAgent], metadata: AgentMetadata) -> None:
        """Register an agent class with its metadata."""
        key = f"{metadata.agent_type.value}:{metadata.name}"
        self._agents[key] = agent_class
        self._metadata[key] = metadata

    def unregister(self, agent_type: AgentType, name: str) -> None:
        """Unregister an agent."""
        key = f"{agent_type.value}:{name}"
        self._agents.pop(key, None)
        self._metadata.pop(key, None)

    def get_agent(self, agent_type: AgentType, name: str) -> Optional[Type[BaseAgent]]:
        """Get an agent class by type and name."""
        key = f"{agent_type.value}:{name}"
        return self._agents.get(key)

    def get_agents_by_type(self, agent_type: AgentType) -> List[Type[BaseAgent]]:
        """Get all agents of a specific type."""
        return [
            agent_class
            for key, agent_class in self._agents.items()
            if key.startswith(f"{agent_type.value}:")
        ]

    def get_compatible_agents(
        self, task: str, context: Dict[str, str], tool: Optional[str] = None
    ) -> List[tuple[Type[BaseAgent], AgentMetadata]]:
        """Get agents compatible with the given task, context and tool."""
        compatible = []

        for key, agent_class in self._agents.items():
            metadata = self._metadata[key]

            # Filter by tool compatibility if specified
            if tool and tool not in metadata.supported_tools:
                continue

            # Check if agent can handle the context (languages, frameworks)
            technologies = context.get("technologies", [])
            if technologies:
                has_compatible_tech = any(
                    any(
                        tech in cap.supported_languages + cap.supported_frameworks
                        for cap in metadata.capabilities
                    )
                    for tech in technologies
                )
                if not has_compatible_tech:
                    continue

            compatible.append((agent_class, metadata))

        # Sort by quality score and usage
        compatible.sort(key=lambda x: (x[1].quality_score, x[1].usage_count), reverse=True)
        return compatible

    def get_all_metadata(self) -> Dict[str, AgentMetadata]:
        """Get metadata for all registered agents."""
        return self._metadata.copy()

    def update_usage(self, agent_type: AgentType, name: str) -> None:
        """Update usage count for an agent."""
        key = f"{agent_type.value}:{name}"
        if key in self._metadata:
            self._metadata[key].usage_count += 1

    def update_quality_score(self, agent_type: AgentType, name: str, score: float) -> None:
        """Update quality score for an agent."""
        key = f"{agent_type.value}:{name}"
        if key in self._metadata:
            self._metadata[key].quality_score = max(0.0, min(10.0, score))


# Global registry instance
_global_registry = AgentRegistry()


def get_global_registry() -> AgentRegistry:
    """Get the global agent registry instance."""
    return _global_registry
