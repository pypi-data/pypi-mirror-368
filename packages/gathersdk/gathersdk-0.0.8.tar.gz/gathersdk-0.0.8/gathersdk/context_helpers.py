"""
Context Helpers for Knowledge Graph Integration

Provides utilities to automatically set up knowledge graph support in AgentContext.
"""

import logging
from typing import Optional
from .agent import AgentContext
from .knowledge_graph import KnowledgeGraphManager, KGStorageBackend
from .storage import create_storage_backend

logger = logging.getLogger(__name__)


def ensure_kg_manager(context: AgentContext, storage_backend: Optional[KGStorageBackend] = None) -> KnowledgeGraphManager:
    """
    Ensure AgentContext has a KnowledgeGraphManager attached.
    
    Creates and caches a KG manager on the context if it doesn't exist.
    
    Args:
        context: The AgentContext to enhance
        storage_backend: Optional custom storage backend
        
    Returns:
        The KG manager attached to the context
    """
    if not hasattr(context, '_kg_manager'):
        if storage_backend:
            context._kg_manager = KnowledgeGraphManager(storage_backend)
        else:
            # Use in-memory storage by default
            context._kg_manager = KnowledgeGraphManager()
    
    return context._kg_manager


def init_persistent_kg(context: AgentContext, db_path: str = None) -> KnowledgeGraphManager:
    """
    Initialize persistent knowledge graph storage for an AgentContext.
    
    Args:
        context: The AgentContext to enhance
        db_path: Path to DuckDB file (defaults to in-memory if None)
        
    Returns:
        KG manager with DuckDB storage
    """
    storage = create_storage_backend("duckdb", db_path=db_path or ":memory:")
    context._kg_manager = KnowledgeGraphManager(storage)
    return context._kg_manager


async def render_kg_context(context: AgentContext, max_searches: int = 2, max_actions: int = 5) -> str:
    """
    Render knowledge graph as agent-readable context string.
    
    Args:
        context: AgentContext with KG data
        max_searches: Maximum recent searches to show
        max_actions: Maximum recent actions to show
        
    Returns:
        Formatted context string for agent instructions
    """
    kg_manager = ensure_kg_manager(context)
    return await kg_manager.render_context(max_searches, max_actions)


async def get_kg_stats(context: AgentContext) -> dict:
    """Get knowledge graph statistics for the given context"""
    kg_manager = ensure_kg_manager(context)
    return await kg_manager.get_stats()


# Convenience functions for common KG operations
async def add_search_to_kg(context: AgentContext, query: str, results: str, search_type: str = "web") -> str:
    """Add search results to context's knowledge graph"""
    kg_manager = ensure_kg_manager(context)
    return await kg_manager.add_search(query, results, search_type)


async def add_entity_to_kg(context: AgentContext, name: str, entity_type: str, properties: dict = None) -> str:
    """Add entity to context's knowledge graph"""
    kg_manager = ensure_kg_manager(context)
    return await kg_manager.add_entity(name, entity_type, properties)


async def add_function_call_to_kg(context: AgentContext, function_name: str, args: dict, result: str) -> str:
    """Add function call to context's knowledge graph"""
    kg_manager = ensure_kg_manager(context)
    return await kg_manager.add_function_call(function_name, args, result)


# KG Visualization Helpers
async def render_kg_snapshot(context: AgentContext, snapshot_context: str = "") -> str:
    """
    Render a visual snapshot of the knowledge graph state
    
    Args:
        context: AgentContext with KG data
        snapshot_context: Context string (e.g., "after search", "before response")
        
    Returns:
        Visual representation of current KG state
    """
    from .visualization import render_kg_snapshot
    kg_manager = ensure_kg_manager(context)
    return await render_kg_snapshot(kg_manager, snapshot_context)


async def print_kg_snapshot(context: AgentContext, snapshot_context: str = "") -> None:
    """
    Print a visual snapshot of the knowledge graph state to logs
    
    Args:
        context: AgentContext with KG data  
        snapshot_context: Context string for the snapshot
    """
    snapshot = await render_kg_snapshot(context, snapshot_context)
    logger.info(f"\n{snapshot}")


async def get_kg_compact_summary(context: AgentContext) -> str:
    """Get a compact one-line summary of KG state"""
    from .visualization import KGVisualizer
    kg_manager = ensure_kg_manager(context)
    visualizer = KGVisualizer(kg_manager)
    return await visualizer.render_compact_summary()


async def dump_kg_state(context: AgentContext) -> str:
    """Get complete structured dump of KG for debugging"""
    from .visualization import KGVisualizer
    kg_manager = ensure_kg_manager(context)
    visualizer = KGVisualizer(kg_manager)
    return await visualizer.render_structured_dump()


def format_conversation_history(agent_context: AgentContext, max_messages: int = 10) -> str:
    """
    Format conversation history for agents using custom dependencies.
    
    This is a convenience function for agents that don't use AgentContext directly
    but store it in custom dependency objects (like SearchBrowseGraph.agent_context).
    
    Args:
        agent_context: The AgentContext object containing conversation history
        max_messages: Maximum number of recent messages to include (default: 10)
        
    Returns:
        Formatted string with conversation history or empty string if no history
        
    Example:
        # For agents with custom dependencies like Deep Agent:
        if ctx.deps.agent_context:
            history = format_conversation_history(ctx.deps.agent_context, 5)
            return f"{history}Current user: {ctx.deps.agent_context.user.display_name}"
    """
    if not agent_context:
        return ""
        
    return agent_context.format_conversation_history(max_messages)