"""
Cross-tool communication protocols for agent coordination.
"""

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MessageType(Enum):
    """Types of messages that can be sent between agents/tools."""

    AGENT_REQUEST = "agent_request"
    AGENT_RESPONSE = "agent_response"
    CONTEXT_SHARE = "context_share"
    COORDINATION = "coordination"
    STATUS_UPDATE = "status_update"
    ERROR = "error"
    HANDOFF = "handoff"


class MessagePriority(Enum):
    """Message priority levels."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class AgentMessage(BaseModel):
    """A message between agents or tools."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType
    priority: MessagePriority = MessagePriority.NORMAL
    sender_id: str
    receiver_id: Optional[str] = None  # None for broadcast
    timestamp: datetime = Field(default_factory=datetime.now)
    payload: Dict[str, Any] = Field(default_factory=dict)
    context: Dict[str, Any] = Field(default_factory=dict)
    requires_response: bool = False
    correlation_id: Optional[str] = None  # For request/response pairs


class CommunicationChannel(ABC):
    """Abstract base for communication channels between tools."""

    @abstractmethod
    async def send_message(self, message: AgentMessage) -> bool:
        """Send a message through this channel."""
        pass

    @abstractmethod
    async def receive_message(self) -> Optional[AgentMessage]:
        """Receive a message from this channel."""
        pass

    @abstractmethod
    async def subscribe(self, message_types: List[MessageType]) -> None:
        """Subscribe to specific message types."""
        pass

    @abstractmethod
    async def unsubscribe(self, message_types: List[MessageType]) -> None:
        """Unsubscribe from message types."""
        pass


class InMemoryChannel(CommunicationChannel):
    """In-memory communication channel for same-process communication."""

    def __init__(self):
        self._message_queue: List[AgentMessage] = []
        self._subscribers: Dict[str, List[MessageType]] = {}

    async def send_message(self, message: AgentMessage) -> bool:
        """Send message to the queue."""
        self._message_queue.append(message)
        return True

    async def receive_message(self) -> Optional[AgentMessage]:
        """Get next message from queue."""
        if self._message_queue:
            return self._message_queue.pop(0)
        return None

    async def subscribe(self, message_types: List[MessageType]) -> None:
        """Subscribe to message types."""
        # Implementation for filtering would go here
        pass

    async def unsubscribe(self, message_types: List[MessageType]) -> None:
        """Unsubscribe from message types."""
        # Implementation for filtering would go here
        pass


class WebSocketChannel(CommunicationChannel):
    """WebSocket-based communication channel for remote tools."""

    def __init__(self, websocket_url: str):
        self.websocket_url = websocket_url
        self.websocket = None

    async def connect(self) -> bool:
        """Connect to WebSocket server."""
        # Implementation would use websockets library
        pass

    async def disconnect(self) -> None:
        """Disconnect from WebSocket server."""
        pass

    async def send_message(self, message: AgentMessage) -> bool:
        """Send message via WebSocket."""
        # Implementation would serialize message and send
        pass

    async def receive_message(self) -> Optional[AgentMessage]:
        """Receive message from WebSocket."""
        # Implementation would receive and deserialize
        pass

    async def subscribe(self, message_types: List[MessageType]) -> None:
        """Subscribe to message types via WebSocket."""
        pass

    async def unsubscribe(self, message_types: List[MessageType]) -> None:
        """Unsubscribe from message types via WebSocket."""
        pass


class MessageBus:
    """Central message bus for routing messages between agents and tools."""

    def __init__(self):
        self._channels: Dict[str, CommunicationChannel] = {}
        self._routes: Dict[str, str] = {}  # receiver_id -> channel_name
        self._message_history: List[AgentMessage] = []

    def add_channel(self, name: str, channel: CommunicationChannel) -> None:
        """Add a communication channel."""
        self._channels[name] = channel

    def remove_channel(self, name: str) -> None:
        """Remove a communication channel."""
        self._channels.pop(name, None)

    def add_route(self, receiver_id: str, channel_name: str) -> None:
        """Add a routing rule for messages."""
        self._routes[receiver_id] = channel_name

    async def send_message(self, message: AgentMessage) -> bool:
        """Send a message through the appropriate channel."""
        # Add to history
        self._message_history.append(message)

        # Handle broadcast messages
        if message.receiver_id is None:
            success = True
            for channel in self._channels.values():
                result = await channel.send_message(message)
                success = success and result
            return success

        # Route to specific receiver
        channel_name = self._routes.get(message.receiver_id)
        if channel_name and channel_name in self._channels:
            return await self._channels[channel_name].send_message(message)

        return False

    async def receive_messages(self, channel_name: str) -> List[AgentMessage]:
        """Receive all pending messages from a channel."""
        if channel_name not in self._channels:
            return []

        messages = []
        channel = self._channels[channel_name]

        while True:
            message = await channel.receive_message()
            if message is None:
                break
            messages.append(message)

        return messages

    def get_message_history(self, limit: int = 100) -> List[AgentMessage]:
        """Get recent message history."""
        return self._message_history[-limit:]


class AgentCoordinator:
    """Coordinates communication between agents and tools."""

    def __init__(self, message_bus: MessageBus):
        self.message_bus = message_bus
        self.active_conversations: Dict[str, List[AgentMessage]] = {}

    async def request_agent_collaboration(
        self, requester_id: str, target_agent_type: str, task: str, context: Dict[str, Any]
    ) -> str:
        """Request collaboration from another agent."""
        correlation_id = str(uuid.uuid4())

        message = AgentMessage(
            message_type=MessageType.AGENT_REQUEST,
            priority=MessagePriority.HIGH,
            sender_id=requester_id,
            receiver_id=target_agent_type,
            payload={"task": task, "context": context},
            requires_response=True,
            correlation_id=correlation_id,
        )

        await self.message_bus.send_message(message)
        self.active_conversations[correlation_id] = [message]

        return correlation_id

    async def respond_to_request(
        self, original_correlation_id: str, responder_id: str, response: Dict[str, Any]
    ) -> None:
        """Respond to an agent request."""
        response_message = AgentMessage(
            message_type=MessageType.AGENT_RESPONSE,
            priority=MessagePriority.HIGH,
            sender_id=responder_id,
            payload=response,
            correlation_id=original_correlation_id,
        )

        await self.message_bus.send_message(response_message)

        if original_correlation_id in self.active_conversations:
            self.active_conversations[original_correlation_id].append(response_message)

    async def share_context(
        self, sender_id: str, context: Dict[str, Any], target_agents: Optional[List[str]] = None
    ) -> None:
        """Share context information with other agents."""
        message = AgentMessage(
            message_type=MessageType.CONTEXT_SHARE,
            priority=MessagePriority.NORMAL,
            sender_id=sender_id,
            payload={"shared_context": context},
            receiver_id=None if target_agents is None else ",".join(target_agents),
        )

        await self.message_bus.send_message(message)

    async def handoff_task(
        self,
        current_agent_id: str,
        target_agent_id: str,
        task: str,
        context: Dict[str, Any],
        reason: str,
    ) -> None:
        """Hand off a task from one agent to another."""
        message = AgentMessage(
            message_type=MessageType.HANDOFF,
            priority=MessagePriority.HIGH,
            sender_id=current_agent_id,
            receiver_id=target_agent_id,
            payload={"task": task, "context": context, "handoff_reason": reason},
            requires_response=True,
        )

        await self.message_bus.send_message(message)
