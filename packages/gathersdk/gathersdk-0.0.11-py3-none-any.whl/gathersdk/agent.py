"""
GatherChat Agent SDK - Base Agent Class and Context Models
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, AsyncIterator
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import logging


# === CONTEXT MODELS (Aligned with server schemas) ===

class UserContext(BaseModel):
    """User information for agent context"""
    user_id: str
    username: str
    display_name: Optional[str] = None


class ChatContext(BaseModel):
    """Chat information for agent context"""
    chat_id: str
    name: str
    creator_id: str
    created_at: datetime
    participants: List[UserContext] = []
    email_address: Optional[str] = None


class MessageContext(BaseModel):
    """Message information for agent context"""
    id: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    content: str
    message_type: str
    agent_name: Optional[str] = None
    created_at: datetime


class AgentContext(BaseModel):
    """
    Standardized context object passed to all agents.
    
    This context provides everything an agent needs to understand
    the current conversation and respond appropriately.
    """
    user: UserContext
    chat: ChatContext
    prompt: str
    conversation_history: List[MessageContext] = Field(
        default=[],
        description="Recent messages in the chat"
    )
    invocation_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)
    session_data: Dict[str, Any] = Field(default_factory=dict)
    knowledge_graph: Dict[str, Any] = Field(
        default_factory=dict,
        description="Runtime knowledge graph built from function calls"
    )
    
    def format_conversation_history(self, max_messages: int = 10) -> str:
        """
        Format conversation history into a standardized string for agent instructions.
        
        Args:
            max_messages: Maximum number of recent messages to include (default: 10)
            
        Returns:
            Formatted string with conversation history or empty string if no history
            
        Example:
            >>> ctx.format_conversation_history(5)
            "\\n\\n--- CONVERSATION HISTORY ---\\n
            User: Hello there
            Agent(search): I'll help you search for information
            User: Find python tutorials
            --- END HISTORY ---\\n\\n"
        """
        if not self.conversation_history:
            return ""
        
        # Take the last N messages
        recent_messages = self.conversation_history[-max_messages:]
        
        # Build the formatted history
        history_lines = ["\\n\\n--- CONVERSATION HISTORY ---"]
        
        for msg in recent_messages:
            # Determine the author display name
            if msg.username:
                author = msg.username
            elif msg.agent_name:
                author = f"Agent({msg.agent_name})"
            else:
                author = "System"
            
            # Add the formatted message
            history_lines.append(f"{author}: {msg.content}")
        
        history_lines.append("--- END HISTORY ---\\n\\n")
        
        return "\\n".join(history_lines)


# === BASE AGENT CLASS ===

class BaseAgent(ABC):
    """
    Base class for all GatherChat agents.
    
    Inherit from this class to create your own agent.
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize the agent.
        
        Args:
            name: The agent's name (must be unique)
            description: A brief description of what the agent does
        """
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"agent.{name}")
    
    @abstractmethod
    async def process(self, context: AgentContext) -> str:
        """
        Process a message and return a response.
        
        This is the main method you need to implement. It receives
        the full context of the conversation and should return a
        text response.
        
        Args:
            context: The agent context containing all relevant information
            
        Returns:
            The agent's text response
        """
        pass
    
    async def process_streaming(self, context: AgentContext) -> AsyncIterator[str]:
        """
        Process a message and yield response chunks for streaming.
        
        Override this method if your agent supports streaming responses.
        By default, it yields the complete response from process().
        
        Args:
            context: The agent context containing all relevant information
            
        Yields:
            Response text chunks
        """
        # Default implementation: yield complete response
        response = await self.process(context)
        yield response
    
    def validate_context(self, context: AgentContext) -> None:
        """
        Validate the context before processing.
        
        Override this method to add custom validation logic.
        Raise ValueError if the context is invalid.
        
        Args:
            context: The agent context to validate
            
        Raises:
            ValueError: If the context is invalid
        """
        if not context.prompt.strip():
            raise ValueError("Prompt cannot be empty")
    
    async def initialize(self) -> None:
        """
        Initialize the agent (e.g., load models, connect to services).
        
        This method is called once when the agent starts up.
        Override it if your agent needs initialization.
        """
        pass
    
    async def cleanup(self) -> None:
        """
        Clean up resources (e.g., close connections, free memory).
        
        This method is called when the agent shuts down.
        Override it if your agent needs cleanup.
        """
        pass


# === HELPER CLASSES ===

class AgentResponse(BaseModel):
    """Standard response format for agents"""
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    streaming: bool = False


class AgentError(BaseModel):
    """Standard error format for agents"""
    error: str
    error_type: str = "processing_error"
    details: Optional[Dict[str, Any]] = None