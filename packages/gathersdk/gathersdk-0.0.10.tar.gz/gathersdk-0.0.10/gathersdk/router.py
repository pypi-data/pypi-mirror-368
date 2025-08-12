"""
Message Router - Clean interface for routing GatherChat messages to handlers
"""

import asyncio
import logging
from typing import Callable, Awaitable, Union, Optional, Protocol
from .agent import BaseAgent, AgentContext

logger = logging.getLogger(__name__)

# Protocol that clearly defines the expected message handler signature
class MessageHandler(Protocol):
    """
    Protocol for message handler functions.
    
    Your function must match this signature:
    async def your_function(ctx: AgentContext) -> str
    """
    def __call__(self, ctx: AgentContext) -> Union[str, Awaitable[str]]: ...

# For backwards compatibility
MessageHandlerType = Callable[[AgentContext], Union[str, Awaitable[str]]]


class MessageRouter:
    """
    Message router for GatherChat agents, inspired by pydantic-ai.
    
    Routes incoming messages to your handlers with rich context.
    
    Usage:
        router = MessageRouter()
        
        @router.on_message
        async def handle(ctx: AgentContext) -> str:
            # ctx: Rich context with user, chat, conversation history, etc.
            return f"Hello {ctx.user.display_name}! You said: {ctx.prompt}"
        
        router.run()
    """
    
    def __init__(self):
        self.name = "MyAgent"  # Default name
        self.description = ""  # Default description  
        self._message_handler: Optional[MessageHandler] = None
    
    def on_message(self, handler: MessageHandler) -> MessageHandler:
        """
        Decorator to register message handler.
        
        Your function must have this exact signature:
        
        @router.on_message
        async def your_function(ctx: AgentContext) -> str:
            # ctx: Rich context containing:
            #   - ctx.user: User who sent the message (username, display_name, etc.)
            #   - ctx.chat: Chat information (id, name, participants, etc.)
            #   - ctx.prompt: The message text content
            #   - ctx.conversation_history: Recent messages for context
            #   - ctx.invocation_id: Unique ID for this invocation
            return "Your response"
        """
        self._message_handler = handler
        return handler
    
    def run(self, **kwargs):
        """Run the agent - connects to GatherChat and handles messages"""
        if not self._message_handler:
            raise ValueError(
                "No message handler registered. Use @router.on_message decorator:\n\n"
                "@router.on_message\n"
                "async def reply(ctx: AgentContext) -> str:\n"
                "    return f'Hello {ctx.user.display_name}! You said: {ctx.prompt}'"
            )
        
        print(f"🤖 Starting message router...")
        
        # Create internal BaseAgent wrapper
        class InternalAgent(BaseAgent):
            def __init__(self, simple_agent: MessageRouter):
                super().__init__(simple_agent.name, simple_agent.description)
                self.simple_agent = simple_agent
            
            async def process(self, context: AgentContext) -> str:
                handler = self.simple_agent._message_handler
                
                # Call user's handler with full context
                if asyncio.iscoroutinefunction(handler):
                    return await handler(context)
                else:
                    return handler(context)
        
        # Create and run internal agent
        internal_agent = InternalAgent(self)
        
        from .client import run_agent
        run_agent(internal_agent, **kwargs)
    
    def run_sync(self, message: str, user: str = "test") -> str:
        """
        Run a single message synchronously (for testing).
        
        Usage:
            from gatherchat_agent_sdk.agent import AgentContext, UserContext, ChatContext
            from datetime import datetime, timezone
            import uuid
            
            # Create test context
            user_ctx = UserContext(user_id="test", username=user, display_name=user)
            chat_ctx = ChatContext(chat_id="test", name="Test", creator_id="test", 
                                 created_at=datetime.now(timezone.utc), participants=[])
            context = AgentContext(user=user_ctx, chat=chat_ctx, prompt=message, 
                                 conversation_history=[], invocation_id=str(uuid.uuid4()))
            
            result = agent.run_sync("Hello!", "Alice")
            print(result)  # "Hello Alice! You said: Hello!"
        """
        if not self._message_handler:
            raise ValueError(
                "No message handler registered. Use @router.on_message decorator:\n\n"
                "@router.on_message\n"
                "async def reply(ctx: AgentContext) -> str:\n"
                "    return f'Hello {ctx.user.display_name}! You said: {ctx.prompt}'"
            )
        
        # Create a minimal test context
        from .agent import AgentContext, UserContext, ChatContext
        from datetime import datetime, timezone
        import uuid
        
        user_ctx = UserContext(user_id="test", username=user, display_name=user)
        chat_ctx = ChatContext(chat_id="test", name="Test", creator_id="test", 
                             created_at=datetime.now(timezone.utc), participants=[])
        context = AgentContext(user=user_ctx, chat=chat_ctx, prompt=message, 
                             conversation_history=[], invocation_id=str(uuid.uuid4()))
        
        handler = self._message_handler
        
        if asyncio.iscoroutinefunction(handler):
            # Run async handler
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            return loop.run_until_complete(handler(context))
        else:
            # Run sync handler
            return handler(context)