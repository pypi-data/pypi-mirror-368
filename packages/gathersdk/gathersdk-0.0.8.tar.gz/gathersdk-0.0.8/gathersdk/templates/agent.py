#!/usr/bin/env python3
"""
Knowledge Graph Agent - A GatherChat agent with dependency-as-graph pattern
"""

import logging
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from gathersdk import MessageRouter, AgentContext
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Create your GatherChat message router
router = MessageRouter()


# ============= KNOWLEDGE GRAPH DEPENDENCY =============


class DemoGraph(BaseModel):
    """
    Knowledge graph dependency - stores all agent state.
    This IS the agent's brain - all state lives here as structured data.
    """
    # Core state
    current_status: str = "initialized"
    messages: list[str] = Field(default_factory=list)
    hello_count: int = 0
    
    # Example structured data
    user_preferences: dict[str, str] = Field(default_factory=dict)
    session_data: dict[str, str] = Field(default_factory=dict)
    
    # Agent context integration
    agent_context: Optional[AgentContext] = None
    agent_id: str = "demo_agent"
    
    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    def update_timestamp(self):
        """Update the last modified timestamp"""
        self.last_updated = datetime.now(timezone.utc)
    
    @property
    def session_summary(self) -> str:
        """Computed property for current session state"""
        return f"Status: {self.current_status}, Messages: {len(self.messages)}, Hello count: {self.hello_count}"


# ============= TOOL FUNCTIONS =============
# These mutate the DemoGraph directly and return simple strings


async def say_hello_world(
    ctx: RunContext[DemoGraph], 
    greeting_message: str,
    include_timestamp: bool = True
) -> str:
    """
    Example tool that says hello and updates the knowledge graph.
    
    Args:
        ctx: The run context containing our knowledge graph
        greeting_message: The greeting message to use
        include_timestamp: Whether to include current time
    
    Returns:
        Simple string confirmation
    """
    try:
        logger.info(f"👋 Say hello called with: {greeting_message}")
        
        # Mutate the knowledge graph directly
        ctx.deps.hello_count += 1
        ctx.deps.current_status = "greeting_sent"
        
        # Create timestamped message
        timestamp_part = f" at {datetime.now().strftime('%H:%M:%S')}" if include_timestamp else ""
        full_message = f"{greeting_message}{timestamp_part}"
        
        # Store in knowledge graph
        ctx.deps.messages.append(full_message)
        ctx.deps.session_data["last_greeting"] = full_message
        ctx.deps.update_timestamp()
        
        logger.info(f"✅ Hello sent successfully (count: {ctx.deps.hello_count})")
        
        # Return simple string confirmation
        return f"✅ Hello sent: '{full_message}' (total greetings: {ctx.deps.hello_count})"
        
    except Exception as e:
        logger.error(f"❌ Say hello failed: {e}")
        return f"❌ Failed to say hello: {str(e)}"


# Initialize Pydantic AI agent with knowledge graph dependency
pydantic_agent = Agent(
    "openai:gpt-4o",
    deps_type=DemoGraph,  # Use knowledge graph as dependency type
    tools=[say_hello_world],  # Add our example tool
    system_prompt="You are a helpful AI assistant with a knowledge graph memory. Use your tools to interact with users and remember information across conversations."
)


@pydantic_agent.instructions
def dynamic_instructions(ctx: RunContext[DemoGraph]) -> str:
    """
    Dynamic instructions based on knowledge graph state and chat context.
    This gives the AI rich information about the current conversation and its memory.
    """
    
    # Get conversation history from agent context
    conversation_history = ""
    if ctx.deps.agent_context:
        conversation_history = ctx.deps.agent_context.format_conversation_history(5)
    
    # Get current knowledge graph state
    try:
        graph_summary = ctx.deps.session_summary
        recent_messages = ctx.deps.messages[-3:] if ctx.deps.messages else []
        preferences = ctx.deps.user_preferences
    except Exception as e:
        logger.error(f"❌ Error reading knowledge graph: {e}")
        graph_summary = "Error reading graph state"
        recent_messages = []
        preferences = {}

    return f"""{conversation_history}

KNOWLEDGE GRAPH STATE:
- {graph_summary}
- Recent messages: {recent_messages}
- User preferences: {preferences}

INSTRUCTIONS:
- Use your say_hello_world tool when greeting users
- Remember information across conversations using your knowledge graph
- Reference previous interactions when appropriate
- Your current status: {ctx.deps.current_status}
- You've sent {ctx.deps.hello_count} greetings so far"""


@router.on_message
async def reply(ctx: AgentContext) -> str:
    """
    Handle incoming messages using Pydantic AI with knowledge graph pattern.

    The knowledge graph maintains state across conversations while AgentContext
    provides the current conversation context.
    """
    user_name = ctx.user.display_name or ctx.user.username

    try:
        # Create or get existing knowledge graph for this chat/user
        # In production, you might load this from storage
        demo_graph = DemoGraph(
            agent_context=ctx,
            agent_id="demo_agent"
        )
        
        # Store user info in knowledge graph
        if user_name:
            demo_graph.user_preferences["user_name"] = user_name
        if ctx.chat.name:
            demo_graph.session_data["chat_name"] = ctx.chat.name
        
        # Run the Pydantic AI agent with knowledge graph dependency
        result = await pydantic_agent.run(ctx.prompt, deps=demo_graph)
        return result.output
    except Exception as e:
        logging.error(f"Error running Pydantic AI: {e}")
        return f"Sorry {user_name}, I encountered an error processing your message."


if __name__ == "__main__":
    print("🤖 Starting knowledge graph agent...")
    print("📍 Using model: gpt-4o")
    print("💡 Set PYDANTIC_AI_MODEL environment variable to use a different model")
    print("💡 Set OPENAI_API_KEY environment variable for OpenAI models")
    print("🧠 Using dependency-as-graph pattern with knowledge graph memory")
    router.run()
