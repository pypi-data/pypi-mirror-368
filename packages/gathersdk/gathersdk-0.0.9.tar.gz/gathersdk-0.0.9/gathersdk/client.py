"""
GatherChat Agent Client - WebSocket connection and message handling
"""

import json
import asyncio
import logging
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import aiohttp

from .auth import SimpleAuth
from .agent import BaseAgent, AgentContext, UserContext, ChatContext, MessageContext

logger = logging.getLogger(__name__)


def parse_datetime(date_str: Optional[str]) -> datetime:
    """
    Parse datetime string from Go server, handling various formats.
    
    Handles:
    - ISO format with 'Z' suffix (e.g., '2024-01-01T12:00:00Z')
    - ISO format without 'Z' (e.g., '2024-01-01T12:00:00')
    - Go zero time value ('0001-01-01T00:00:00Z')
    - None or empty strings
    """
    if not date_str:
        return datetime.now(timezone.utc)
    
    # Handle Go's zero time value
    if date_str.startswith('0001-01-01'):
        return datetime.now(timezone.utc)
    
    # Remove 'Z' suffix if present and add UTC timezone
    if date_str.endswith('Z'):
        date_str = date_str[:-1] + '+00:00'
    
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        logger.warning(f"Could not parse datetime: {date_str}, using current time")
        return datetime.now(timezone.utc)


class AgentClient:
    """
    WebSocket client for GatherChat agents.
    
    Handles:
    - Simple API key authentication
    - WebSocket connection management
    - Message routing to agent
    - Automatic reconnection
    - Heartbeat/keepalive
    """
    
    def __init__(
        self,
        agent: BaseAgent,
        agent_key: str = None,
        api_url: str = None
    ):
        """
        Initialize agent client.
        
        Args:
            agent: Your BaseAgent implementation
            agent_key: Agent API key (default: from GATHERCHAT_AGENT_KEY env)
            api_url: API base URL (default: from GATHERCHAT_API_URL env)
            heartbeat_interval: Seconds between heartbeats (default: 30)
        """
        self.agent = agent
        # Note: Heartbeat removed - WebSocket has built-in ping/pong
        
        # Initialize authentication
        if agent_key and api_url:
            self.auth = SimpleAuth(agent_key, api_url)
        else:
            # Load from environment
            self.auth = SimpleAuth.from_env()
        
        self.websocket: Optional[aiohttp.ClientWebSocketResponse] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.running = False
        self._reconnect_delay = 5
        self.authenticated_agent_name: Optional[str] = None  # Set during authentication (display name)
        self.authenticated_username: Optional[str] = None    # Set during authentication (username for @mentions)
        # Note: Heartbeat task removed
    
    async def connect(self) -> None:
        """Connect to GatherChat WebSocket with agent authentication"""
        try:
            # Create WebSocket session
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            # Get WebSocket URL from server config
            ws_url = await self.auth.get_ws_url()
            logger.info(f"Connecting to WebSocket...")
            
            headers = self.auth.get_auth_headers()
            self.websocket = await self.session.ws_connect(
                ws_url,
                headers=headers
            )
            
            logger.info("WebSocket connected, authenticating...")
            
            # Send authentication event (GoGather format - no welcome message)
            auth_message = {
                "event": "authenticate_with_api_key",
                "data": {
                    "api_key": self.auth.agent_key
                }
            }
            
            await self.websocket.send_json(auth_message)
            
            # Wait for auth confirmation
            auth_response = await self.websocket.receive_json()
            
            # GoGather auth response format: {"event": "authSuccess", "data": {"user_id": "...", "username": "...", "name": "..."}}
            if auth_response.get("event") == "authSuccess":
                data = auth_response.get("data", {})
                # Get the REAL agent name from server (prefer display name over username)
                self.authenticated_agent_name = data.get('name') or data.get('username', 'Unknown')
                self.authenticated_username = data.get('username', 'Unknown')
                logger.info(f"✅ Authenticated as agent: {self.authenticated_agent_name} (@{self.authenticated_username})")
                
                # Initialize the agent
                await self.agent.initialize()
                
            else:
                error_msg = auth_response.get("message", "Authentication failed")
                raise Exception(f"Authentication failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise
    
    # Heartbeat functionality removed - WebSocket has built-in ping/pong
    
    async def disconnect(self) -> None:
        """Disconnect from WebSocket and cleanup"""
        self.running = False
        
        # Note: No heartbeat to stop
        
        # Cleanup agent
        await self.agent.cleanup()
        
        # Close WebSocket
        if self.websocket and not self.websocket.closed:
            await self.websocket.close()
        
        # Close session
        if self.session:
            await self.session.close()
        
        logger.info("Disconnected from GatherChat")
    
    async def _handle_message(self, message: Dict[str, Any]) -> None:
        """Handle incoming WebSocket message"""
        # Handle server message wrapping
        message_type = message.get("type")
        logger.info(f"📨 Message type: {message_type}")
        
        if message_type == "agent_message":
            # Unwrap agent message - server sends: {"type": "agent_message", "event": "...", "data": {...}}
            event = message.get("event")
            data = message.get("data", {})
        elif message_type == "broadcast":
            # Broadcast format - server sends: {"type": "broadcast", "event": "...", "data": {...}}
            event = message.get("event")
            data = message.get("data", {})
        else:
            # Direct event format
            event = message.get("event") 
            data = message.get("data", {})
        
        logger.info(f"🔍 Handling event: {event}")
        
        # Handle new messages (agents get @mentions as regular messages)
        if event == "new_message":
            logger.info(f"🚀 Received message: {data.get('content', '')}")
            
            try:
                # Extract message details
                content = data.get('content', '')
                username = data.get('username', 'Unknown')
                chat_id = data.get('chat_id', '')
                user_id = data.get('user_id', 'unknown')  # Get user_id from broadcast
                target_agent = data.get('target_agent', None)  # Check if this is a direct widget message
                
                # Debug: log agent name check
                logger.info(f"🔍 Checking if '{content}' is for agent '{self.authenticated_agent_name}'")
                
                # Check if this is for this agent
                is_for_agent = False
                
                # Case 1: Direct widget message (has target_agent field)
                if target_agent and target_agent == self.authenticated_agent_name:
                    logger.info(f"🎯 Direct widget message for {self.authenticated_agent_name}")
                    is_for_agent = True
                    message = content  # Use content as-is
                
                # Case 2: Regular @mention
                elif content.startswith(f"@{self.authenticated_username} "):
                    # Extract the actual message after @username (people @mention using username, not display name)
                    message = content[len(f"@{self.authenticated_username} "):].strip()
                    is_for_agent = True
                
                if is_for_agent:
                    logger.info(f"🧠 Detected message from {username}: '{message}'")
                    logger.info(f"⏳ Waiting for server to send rich context via agent_invoke_streaming event...")
                    
                    # The server will automatically send context via agent_invoke_streaming event
                    # when it detects an SDK agent invocation. No need to request it.
                else:
                    logger.debug(f"Message not for this agent: {content}")
                
            except Exception as e:
                logger.error(f"❌ Error processing message: {e}")
        
        # Handle GoGather agent invocation (replaces FastAPI agent_invoke_streaming)
        elif event == "agent_invocation":
            logger.info(f"🎯 Received GoGather agent invocation for user: {data.get('context', {}).get('user', {}).get('username')}")
            
            try:
                # Parse the GoGather invocation format
                
                invocation_id = data.get('invocation_id')
                context_data = data.get('context', {})
                
                # Build AgentContext from GoGather server data
                user_data = context_data.get('user', {})
                user_context = UserContext(
                    user_id=user_data.get('user_id'),
                    username=user_data.get('username'),
                    display_name=user_data.get('display_name')
                )
                
                chat_data = context_data.get('chat', {})
                # Parse participants
                participants = []
                for p_data in chat_data.get('participants', []):
                    participants.append(UserContext(
                        user_id=p_data.get('user_id'),
                        username=p_data.get('username'),
                        display_name=p_data.get('display_name')
                    ))
                
                chat_context = ChatContext(
                    chat_id=chat_data.get('chat_id'),
                    name=chat_data.get('name'),
                    creator_id=chat_data.get('creator_id'),
                    created_at=parse_datetime(chat_data.get('created_at')),
                    participants=participants
                )
                
                # Parse conversation history
                conversation_history = []
                for msg_data in context_data.get('conversation_history', []):
                    conversation_history.append(MessageContext(
                        id=msg_data.get('id'),
                        user_id=msg_data.get('user_id'),
                        username=msg_data.get('username'),
                        content=msg_data.get('content'),
                        message_type=msg_data.get('message_type'),
                        agent_name=msg_data.get('agent_name'),
                        created_at=parse_datetime(msg_data.get('created_at'))
                    ))
                
                context = AgentContext(
                    user=user_context,
                    chat=chat_context,
                    prompt=context_data.get('prompt'),
                    conversation_history=conversation_history,
                    invocation_id=invocation_id,
                    metadata=context_data.get('metadata', {})
                )
                
                logger.info(f"🧠 Processing GoGather invocation: {len(conversation_history)} messages, {len(participants)} participants")
                
                # Process with the agent using the rich context
                response = await self.agent.process(context)
                logger.info(f"💬 Agent response: '{response}'")
                
                # Send response back using GoGather agent_response format
                await self.websocket.send_json({
                    "event": "agent_response",
                    "data": {
                        "invocation_id": invocation_id,
                        "response": response,
                        "error": ""
                    }
                })
                
                logger.info(f"✅ Sent GoGather agent response for invocation {invocation_id}")
                
            except Exception as e:
                logger.error(f"❌ Error processing GoGather invocation: {e}")
                import traceback
                logger.error(traceback.format_exc())
                
                # Send error response using GoGather format
                await self.websocket.send_json({
                    "event": "agent_response",
                    "data": {
                        "invocation_id": data.get('invocation_id', 'unknown'),
                        "response": "",
                        "error": str(e)
                    }
                })
        
        # Handle legacy FastAPI streaming (for backwards compatibility)
        elif event == "agent_invoke_streaming":
            logger.info(f"Received legacy FastAPI streaming invocation")
            
            try:
                # Parse context
                context = AgentContext(**data)
                
                # Validate context
                self.agent.validate_context(context)
                
                # Process with streaming
                async for chunk in self.agent.process_streaming(context):
                    await self.websocket.send_json({
                        "event": "agent_response_chunk",
                        "data": {
                            "invocation_id": context.invocation_id,
                            "chunk": chunk,
                            "done": False
                        }
                    })
                
                # Send completion
                await self.websocket.send_json({
                    "event": "agent_response_chunk",
                    "data": {
                        "invocation_id": context.invocation_id,
                        "chunk": "",
                        "done": True,
                        "success": True
                    }
                })
                
                logger.info("✅ Completed legacy FastAPI streaming response")
                
            except Exception as e:
                logger.error(f"Error in legacy FastAPI streaming: {e}")
                
                # Send error
                await self.websocket.send_json({
                    "event": "agent_response_chunk",
                    "data": {
                        "invocation_id": data.get("invocation_id"),
                        "error": str(e),
                        "done": True,
                        "success": False
                    }
                })
        
        # Note: Heartbeat handling removed
        
        # Handle errors
        elif event == "error":
            logger.error(f"Server error: {data.get('message', 'Unknown error')}")
        
        # Handle disconnection request
        elif event == "disconnect":
            logger.info(f"Server requested disconnect: {data.get('reason', 'No reason given')}")
            self.running = False
        
        else:
            logger.debug(f"Received event: {event}")
    
    async def run(self) -> None:
        """
        Run the agent client with automatic reconnection.
        This is the main entry point - call this to start your agent.
        """
        self.running = True
        reconnect_attempts = 0
        max_reconnect_delay = 60
        
        print(f"🤖 Starting message router...")
        print(f"📡 Waiting for invocations...")
        logger.info(f"🤖 Starting message router...")
        logger.info(f"📡 Waiting for invocations...")
        
        while self.running:
            try:
                # Connect to WebSocket
                await self.connect()
                
                # Reset reconnection attempts on successful connection
                reconnect_attempts = 0
                
                # Message handling loop
                async for msg in self.websocket:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        try:
                            data = json.loads(msg.data)
                            print(f"📥 Received raw message: {data}")
                            logger.info(f"📥 Received raw message: {data}")
                            await self._handle_message(data)
                        except json.JSONDecodeError:
                            print(f"Invalid JSON received: {msg.data}")
                            logger.error(f"Invalid JSON received: {msg.data}")
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        logger.error(f"WebSocket error: {self.websocket.exception()}")
                        break
                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        logger.info("WebSocket connection closed")
                        break
                
            except Exception as e:
                logger.error(f"Connection error: {e}")
            
            finally:
                # Cleanup current connection
                if self.websocket and not self.websocket.closed:
                    await self.websocket.close()
                
                # Note: No heartbeat to stop
                
                # Reconnect if still running
                if self.running:
                    # Exponential backoff with max delay
                    delay = min(self._reconnect_delay * (2 ** reconnect_attempts), max_reconnect_delay)
                    reconnect_attempts += 1
                    
                    logger.info(f"Reconnecting in {delay} seconds (attempt {reconnect_attempts})...")
                    await asyncio.sleep(delay)
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()


def run_agent(agent: BaseAgent, **kwargs):
    """
    Convenience function to run an agent.
    
    Args:
        agent: Your BaseAgent implementation
        **kwargs: Additional arguments for AgentClient
    
    Example:
        from gathersdk import BaseAgent, AgentContext, run_agent
        
        class MyAgent(BaseAgent):
            async def process(self, context: AgentContext) -> str:
                return f"Hello {context.user.username}!"
        
        if __name__ == "__main__":
            agent = MyAgent("my-agent", "A friendly greeting agent")
            run_agent(agent)
    """
    async def main():
        async with AgentClient(agent, **kwargs) as client:
            await client.run()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Agent stopped by user")
    except Exception as e:
        logger.error(f"Agent error: {e}")
        raise