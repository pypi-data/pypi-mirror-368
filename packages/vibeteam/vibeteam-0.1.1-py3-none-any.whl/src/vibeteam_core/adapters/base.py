"""
Base tool adapter interfaces for different coding environments.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field


class ToolCapability(Enum):
    """Capabilities that different tools can provide."""

    FILE_EDITING = "file_editing"
    REAL_TIME_EDITING = "real_time_editing"
    MULTI_FILE_OPERATIONS = "multi_file_operations"
    IDE_INTEGRATION = "ide_integration"
    DEBUGGING = "debugging"
    GIT_INTEGRATION = "git_integration"
    TERMINAL_ACCESS = "terminal_access"
    WEB_BROWSING = "web_browsing"
    CODE_EXECUTION = "code_execution"
    SYNTAX_HIGHLIGHTING = "syntax_highlighting"
    AUTO_COMPLETION = "auto_completion"
    REFACTORING_TOOLS = "refactoring_tools"
    TESTING_FRAMEWORK = "testing_framework"


class ToolCommand(BaseModel):
    """A command that can be executed by a tool."""

    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    capabilities_required: List[ToolCapability] = Field(default_factory=list)


class ToolAdapter(ABC):
    """Abstract base class for tool adapters."""

    def __init__(self, tool_name: str, capabilities: List[ToolCapability]):
        self.tool_name = tool_name
        self.capabilities = capabilities
        self.is_connected = False

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the tool."""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from the tool."""
        pass

    @abstractmethod
    async def execute_command(self, command: ToolCommand) -> Dict[str, Any]:
        """Execute a command using the tool."""
        pass

    @abstractmethod
    def get_available_commands(self) -> List[ToolCommand]:
        """Get list of commands available in this tool."""
        pass

    @abstractmethod
    def supports_capability(self, capability: ToolCapability) -> bool:
        """Check if tool supports a specific capability."""
        pass

    def can_execute(self, command: ToolCommand) -> bool:
        """Check if this adapter can execute the given command."""
        return all(self.supports_capability(cap) for cap in command.capabilities_required)

    async def send_agent_result(self, result: Dict[str, Any]) -> bool:
        """Send agent result back to the tool."""
        # Default implementation - subclasses can override
        return True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(tool={self.tool_name})>"
