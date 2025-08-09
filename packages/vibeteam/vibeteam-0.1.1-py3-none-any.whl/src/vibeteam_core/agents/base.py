"""
Base agent classes and interfaces for the Vibeteam framework.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class AgentType(Enum):
    """Types of specialized agents available in the framework."""

    BACKEND = "backend_specialist"
    FRONTEND = "frontend_specialist"
    FULLSTACK = "fullstack_engineer"
    RESEARCHER = "web_researcher"
    ANALYZER = "code_analyzer"
    TESTER = "test_engineer"
    DEVOPS = "devops_specialist"
    SECURITY = "security_specialist"
    DOCUMENTATION = "documentation_specialist"
    REFACTOR = "refactoring_specialist"
    PERFORMANCE = "performance_specialist"


class AgentCapability(BaseModel):
    """Describes what an agent is capable of doing."""

    name: str
    description: str
    supported_languages: List[str] = Field(default_factory=list)
    supported_frameworks: List[str] = Field(default_factory=list)
    supported_tools: List[str] = Field(default_factory=list)
    complexity_level: int = Field(ge=1, le=5, default=1)
    priority: int = Field(ge=1, le=10, default=5)


class AgentResult(BaseModel):
    """Result returned by an agent after execution."""

    agent_type: AgentType
    status: str  # "success", "failed", "partial"
    result: Dict[str, Any]
    recommendations: List[str] = Field(default_factory=list)
    next_actions: List[str] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    execution_time: float = 0.0
    errors: List[str] = Field(default_factory=list)


class BaseAgent(ABC):
    """Abstract base class for all agents in the Vibeteam framework."""

    def __init__(self, agent_type: AgentType, capabilities: List[AgentCapability]):
        self.agent_type = agent_type
        self.capabilities = capabilities
        self.status = "initialized"

    @abstractmethod
    async def can_handle(self, task: str, context: Dict[str, Any]) -> bool:
        """Determine if this agent can handle the given task and context."""
        pass

    @abstractmethod
    async def execute(self, task: str, context: Dict[str, Any]) -> AgentResult:
        """Execute the given task with the provided context."""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[AgentCapability]:
        """Return list of capabilities this agent supports."""
        pass

    def get_priority(self, task: str, context: Dict[str, Any]) -> int:
        """Calculate priority for this agent given the task and context."""
        base_priority = 5

        # Higher priority for matching agent type
        for capability in self.capabilities:
            if any(
                lang in context.get("technologies", []) for lang in capability.supported_languages
            ):
                base_priority += 2
            if any(fw in context.get("technologies", []) for fw in capability.supported_frameworks):
                base_priority += 2

        return min(base_priority, 10)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(type={self.agent_type.value})>"
