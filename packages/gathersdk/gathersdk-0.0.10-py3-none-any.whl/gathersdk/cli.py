#!/usr/bin/env python3
"""
GatherSDK CLI - Simple commands to get started with GatherChat agents
"""

import os
import shutil
import click
import json
import asyncio
import aiohttp
from pathlib import Path
from typing import Optional, Dict, Any
from getpass import getpass

# Get the package directory to find templates
PACKAGE_DIR = Path(__file__).parent
TEMPLATES_DIR = PACKAGE_DIR / "templates"

# Config file for storing auth
CONFIG_DIR = Path.home() / ".gatherchat"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> Dict[str, Any]:
    """Load configuration from file."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to file."""
    CONFIG_DIR.mkdir(exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


async def api_request(method: str, endpoint: str, data: Optional[Dict] = None, token: Optional[str] = None) -> Dict[str, Any]:
    """Make an API request to GatherChat."""
    base_url = os.getenv('GATHERCHAT_API_URL', 'https://gather.is')
    url = f"{base_url.rstrip('/')}/api{endpoint}"
    
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    async with aiohttp.ClientSession() as session:
        async with session.request(method, url, json=data, headers=headers) as response:
            result = await response.json()
            if response.status >= 400:
                raise click.ClickException(f"API error: {result.get('detail', 'Unknown error')}")
            return result


@click.group()
@click.version_option()
def main():
    """
    GatherSDK - Build AI agents for GatherChat in minutes
    
    Get started with: gathersdk init
    """
    pass


@main.command()
@click.option('--force', '-f', is_flag=True, help='Overwrite existing files')
def init(force):
    """
    Initialize a new GatherChat agent project
    
    Creates:
    - agent.py (Pydantic AI example)
    - .env.example (configuration template)
    """
    current_dir = Path.cwd()
    
    # Files to create
    files_to_create = [
        ("agent.py", "agent.py"),
        (".env.example", ".env.example")
    ]
    
    click.echo("🚀 Initializing GatherChat agent project...")
    
    # Check if files already exist
    existing_files = []
    for dest_name, _ in files_to_create:
        dest_path = current_dir / dest_name
        if dest_path.exists():
            existing_files.append(dest_name)
    
    if existing_files and not force:
        click.echo(f"❌ Files already exist: {', '.join(existing_files)}")
        click.echo("   Use --force to overwrite")
        return
    
    # Copy template files
    for dest_name, template_name in files_to_create:
        template_path = TEMPLATES_DIR / template_name
        dest_path = current_dir / dest_name
        
        if not template_path.exists():
            click.echo(f"❌ Template not found: {template_path}")
            continue
            
        try:
            shutil.copy2(template_path, dest_path)
            click.echo(f"✅ Created {dest_name}")
        except Exception as e:
            click.echo(f"❌ Failed to create {dest_name}: {e}")
            continue
    
    # Make agent.py executable
    agent_path = current_dir / "agent.py"
    if agent_path.exists():
        agent_path.chmod(0o755)
    
    click.echo("")
    click.echo("🎉 Project initialized successfully!")
    click.echo("")
    click.echo("Next steps:")
    click.echo("1. Copy .env.example to .env and add your keys:")
    click.echo("   cp .env.example .env")
    click.echo("")
    click.echo("2. Get your agent key from https://gather.is/developer")
    click.echo("")
    click.echo("3. Add your OpenAI API key to .env")
    click.echo("")
    click.echo("4. Run your agent:")
    click.echo("   python agent.py")
    click.echo("")
    click.echo("🤖 Your agent will be live in GatherChat!")


@main.command()
def register():
    """Register a new GatherChat account."""
    click.echo("Welcome to GatherChat! Let's create your account.")
    click.echo("")
    
    # Get user details
    username = click.prompt("Choose a username")
    email = click.prompt("Email address")
    password = getpass("Password: ")
    password_confirm = getpass("Confirm password: ")
    
    if password != password_confirm:
        raise click.ClickException("Passwords don't match")
    
    # Optional fields
    display_name = click.prompt("Display name (optional)", default="", show_default=False)
    
    click.echo("")
    click.echo("Creating your account...")
    
    # Make registration request
    async def do_register():
        try:
            result = await api_request('POST', '/auth/register', {
                'username': username,
                'password': password,
                'email': email,
                'display_name': display_name or None,
                'verification_method': 'email'
            })
            
            if result.get('success'):
                click.echo("✅ Account created successfully!")
                click.echo("")
                click.echo(f"📧 {result.get('message', 'Verification email sent')}")
                click.echo("")
                click.echo("Next steps:")
                click.echo("1. Check your email for verification link")
                click.echo("2. Click the link to verify your account")
                click.echo("3. Run 'gathersdk login' to authenticate")
            else:
                raise click.ClickException(result.get('message', 'Registration failed'))
                
        except Exception as e:
            raise click.ClickException(f"Registration failed: {str(e)}")
    
    asyncio.run(do_register())


@main.command()
def login():
    """Login to your GatherChat account."""
    config = load_config()
    
    if config.get('token'):
        if click.confirm("You're already logged in. Login again?"):
            config = {}
        else:
            return
    
    username = click.prompt("Username")
    password = getpass("Password: ")
    
    async def do_login():
        try:
            result = await api_request('POST', '/auth/login', {
                'username': username,
                'password': password
            })
            
            # Save token
            config['token'] = result['access_token']
            config['username'] = result['username']
            config['participant_id'] = result['participant_id']
            save_config(config)
            
            click.echo("✅ Logged in successfully!")
            click.echo(f"   Username: {result['username']}")
            
        except Exception as e:
            raise click.ClickException(f"Login failed: {str(e)}")
    
    asyncio.run(do_login())


@main.command()
@click.option('--name', prompt='Agent name', help='Unique name for your agent')
@click.option('--description', prompt='Agent description', help='What does your agent do?')
def create_agent(name, description):
    """Create a new agent."""
    config = load_config()
    
    if not config.get('token'):
        raise click.ClickException("Please login first: gathersdk login")
    
    async def do_create():
        try:
            result = await api_request('POST', '/users/me/agents', {
                'agent_name': name,
                'description': description
            }, token=config['token'])
            
            if result.get('success'):
                agent = result['agent']
                client_secret = result['client_secret']
                
                click.echo("✅ Agent created successfully!")
                click.echo("")
                click.echo(f"Agent name: {agent['agent_name']}")
                click.echo(f"Agent ID: {agent['id']}")
                click.echo(f"Description: {agent['description']}")
                click.echo("")
                click.echo("🔑 Your agent key (save this securely!):")
                click.echo(f"   {client_secret}")
                click.echo("")
                
                if agent.get('dev_room'):
                    click.echo(f"📍 Dev room: {agent['dev_room']['name']}")
                    # Generate permalink for dev room
                    permalink = f"https://gather.is/chat/{agent['dev_room']['chat_id']}"
                    click.echo(f"   Permalink: {permalink}")
                
                # Offer to save to .env
                if click.confirm("\nSave agent key to .env file?"):
                    env_path = Path.cwd() / '.env'
                    with open(env_path, 'a') as f:
                        f.write(f"\n# {agent['agent_name']} agent key\n")
                        f.write(f"GATHERCHAT_AGENT_KEY={client_secret}\n")
                    click.echo(f"✅ Saved to {env_path}")
                
            else:
                raise click.ClickException(result.get('message', 'Failed to create agent'))
                
        except Exception as e:
            raise click.ClickException(f"Failed to create agent: {str(e)}")
    
    asyncio.run(do_create())


@main.command()
def list_agents():
    """List your agents."""
    config = load_config()
    
    if not config.get('token'):
        raise click.ClickException("Please login first: gathersdk login")
    
    async def do_list():
        try:
            result = await api_request('GET', '/users/me/agents', token=config['token'])
            
            if result.get('success'):
                agents = result.get('agents', [])
                
                if not agents:
                    click.echo("You don't have any agents yet.")
                    click.echo("Create one with: gathersdk create-agent")
                    return
                
                click.echo(f"Your agents ({len(agents)}):")
                click.echo("")
                
                for agent in agents:
                    click.echo(f"📤 {agent['agent_name']}")
                    click.echo(f"   ID: {agent['id']}")
                    click.echo(f"   Description: {agent['description']}")
                    click.echo(f"   Status: {agent['status']}")
                    if agent.get('dev_room'):
                        permalink = f"https://gather.is/chat/{agent['dev_room']['chat_id']}"
                        click.echo(f"   Dev room: {permalink}")
                    click.echo("")
                    
            else:
                raise click.ClickException(result.get('message', 'Failed to list agents'))
                
        except Exception as e:
            raise click.ClickException(f"Failed to list agents: {str(e)}")
    
    asyncio.run(do_list())


@main.command()
@click.argument('chat_id')
def permalink(chat_id):
    """Get permalink for a chat."""
    config = load_config()
    
    if not config.get('token'):
        raise click.ClickException("Please login first: gathersdk login")
    
    async def do_permalink():
        try:
            result = await api_request('GET', f'/chats/{chat_id}/permalink', token=config['token'])
            
            if result.get('success'):
                click.echo(f"Chat: {result['chat_name']}")
                click.echo(f"Permalink: {result['permalink']}")
                click.echo("")
                click.echo("Share this link to invite others to the chat!")
            else:
                raise click.ClickException(result.get('message', 'Failed to get permalink'))
                
        except Exception as e:
            raise click.ClickException(f"Failed to get permalink: {str(e)}")
    
    asyncio.run(do_permalink())


@main.command()
def whoami():
    """Show current logged in user."""
    config = load_config()
    
    if not config.get('token'):
        click.echo("Not logged in. Use 'gathersdk login' to authenticate.")
        return
    
    click.echo(f"Logged in as: {config.get('username', 'Unknown')}")
    click.echo(f"User ID: {config.get('participant_id', 'Unknown')}")


@main.command()
def logout():
    """Logout from GatherChat."""
    config = load_config()
    
    if not config.get('token'):
        click.echo("Not logged in.")
        return
    
    if click.confirm(f"Logout {config.get('username', 'user')}?"):
        save_config({})
        click.echo("✅ Logged out successfully.")


if __name__ == "__main__":
    main()