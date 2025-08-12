from pydantic import BaseModel
from typing import Any, Protocol

class ChatMessage(BaseModel):
    """Represents a single message in a chat conversation."""
    role: str
    content: str

class AgentProtocol(Protocol):
    """Defines the expected interface for an agent."""
    id: str
    name: str
    description: str
    def run(self, query: str, **kwargs: Any) -> dict[str, Any]:
        """Synchronous execution method."""
    async def arun(self, query: str, **kwargs: Any) -> dict[str, Any]:
        """Asynchronous execution method."""
