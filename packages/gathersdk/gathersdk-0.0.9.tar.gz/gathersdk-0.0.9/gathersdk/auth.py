"""
Simple API Key Authentication for GatherChat Agents
"""

import os
import aiohttp
from typing import Dict, Optional


class SimpleAuth:
    """Simple API key authentication for GoGather agents"""
    
    def __init__(self, agent_key: str, api_base_url: str = None):
        """
        Initialize authentication with agent key.
        
        Args:
            agent_key: The secret agent key provided when creating the agent
            api_base_url: The base URL of the GoGather API (optional, defaults to production)
        """
        self.agent_key = agent_key
        self.api_base_url = api_base_url
        self._ws_url: Optional[str] = None
        
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for HTTP requests"""
        return {
            'Authorization': f'Bearer {self.agent_key}',
            'X-Agent-Key': self.agent_key
        }
    
    async def get_ws_url(self) -> str:
        """
        Get WebSocket URL for GoGather server.
        
        Returns:
            Complete WebSocket URL (GoGather uses API key auth via WebSocket message)
        """
        if self._ws_url:
            return self._ws_url
            
        # Check for environment variable override first
        ws_url = os.getenv('GATHERCHAT_WS_URL')
        if ws_url:
            self._ws_url = ws_url
            return self._ws_url
            
        # Use production URL by default
        if self.api_base_url:
            base_url = self.api_base_url.rstrip('/')
            # Convert HTTP to WebSocket URL
            if base_url.startswith('https://'):
                ws_url = base_url.replace('https://', 'wss://')
            else:
                ws_url = base_url.replace('http://', 'ws://')
            self._ws_url = f"{ws_url}/ws"
        else:
            # Default to production WebSocket URL
            self._ws_url = 'wss://gather.is/ws'
            
        return self._ws_url
    
    async def _fetch_config(self) -> Dict:
        """Fetch configuration from GoGather server (not used in current implementation)."""
        # GoGather doesn't use config endpoints, but keeping for compatibility
        return {
            'websocket_url': 'wss://gather.is/ws',  # Production GoGather WebSocket server
            'api_base_url': 'https://gather.is'
        }
    
    @classmethod
    def from_env(cls) -> 'SimpleAuth':
        """
        Create auth instance from environment variables.
        
        Required environment variables:
        - GATHERCHAT_AGENT_KEY: Your agent's secret key
        
        Optional environment variables:
        - GATHERCHAT_API_URL: The GoGather API URL (defaults to production)
        - GATHERCHAT_WS_URL: Direct WebSocket URL override (e.g., ws://127.0.0.1:8090/ws for local dev)
        
        Returns:
            SimpleAuth instance configured from environment
            
        Raises:
            ValueError: If required environment variables are missing
        """
        # Load .env from current working directory
        from dotenv import load_dotenv
        load_dotenv()
        
        agent_key = os.getenv('GATHERCHAT_AGENT_KEY')
        api_url = os.getenv('GATHERCHAT_API_URL')  # Optional
        
        if not agent_key:
            # Try to load .env again more explicitly
            import os as _os
            env_file = _os.path.join(_os.getcwd(), '.env')
            if _os.path.exists(env_file):
                load_dotenv(env_file)
                agent_key = os.getenv('GATHERCHAT_AGENT_KEY')
            
            if not agent_key:
                raise ValueError(
                    "Missing authentication credentials. "
                    "Please set GATHERCHAT_AGENT_KEY environment variable or create a .env file."
                )
            
        return cls(agent_key=agent_key, api_base_url=api_url)