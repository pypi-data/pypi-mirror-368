"""
Tool Decorators and Utilities for Knowledge Graph Integration

Provides decorators to automatically add knowledge graph tracking to any function.
"""

from functools import wraps
from typing import Any, Callable, Optional, Dict
import time
import logging
from .knowledge_graph import KnowledgeGraphManager

logger = logging.getLogger(__name__)


def with_knowledge_graph(
    entity_type: str = "function_call",
    track_args: bool = True,
    track_result: bool = True,
    result_summary_length: int = 200
):
    """
    Decorator to automatically add knowledge graph tracking to any function.
    
    Args:
        entity_type: Type of entity to create in knowledge graph
        track_args: Whether to store function arguments
        track_result: Whether to store function result summary
        result_summary_length: Max length of result summary to store
    
    Usage:
        @with_knowledge_graph("search_action")
        async def my_search_tool(ctx: RunContext[AgentContext], query: str) -> str:
            # Your tool implementation
            return results
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract AgentContext from function arguments
            ctx = None
            for arg in args:
                if hasattr(arg, 'deps') and hasattr(arg.deps, 'knowledge_graph'):
                    ctx = arg
                    break
            
            if not ctx:
                # No AgentContext found, just run the function normally
                logger.warning(f"No AgentContext found for {func.__name__}, skipping KG tracking")
                return await func(*args, **kwargs)
            
            start_time = time.time()
            
            try:
                # Execute the original function
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Get or create KG manager from context
                if not hasattr(ctx.deps, '_kg_manager'):
                    # Initialize KG manager if not present
                    from .knowledge_graph import InMemoryKGStorage, KnowledgeGraphManager
                    ctx.deps._kg_manager = KnowledgeGraphManager()
                
                kg_manager = ctx.deps._kg_manager
                
                # Prepare arguments for storage
                args_dict = {}
                if track_args:
                    # Store non-context arguments
                    for i, arg in enumerate(args[1:], 1):  # Skip context argument
                        if hasattr(arg, '__dict__'):
                            args_dict[f'arg_{i}'] = str(arg)[:100]  # Truncate long args
                        else:
                            args_dict[f'arg_{i}'] = str(arg)[:100]
                    
                    for key, value in kwargs.items():
                        args_dict[key] = str(value)[:100]
                
                # Store result summary
                result_summary = ""
                if track_result and result:
                    result_summary = str(result)[:result_summary_length]
                
                # Add to knowledge graph
                await kg_manager.add_function_call(
                    function_name=func.__name__,
                    args=args_dict,
                    result=result_summary,
                    execution_time=execution_time
                )
                
                logger.debug(f"🧠 KG tracked: {func.__name__} ({execution_time:.2f}s)")
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                # Track failed function calls too
                if hasattr(ctx.deps, '_kg_manager'):
                    await ctx.deps._kg_manager.add_function_call(
                        function_name=func.__name__,
                        args={"error": str(e)} if track_args else {},
                        result=f"ERROR: {str(e)[:100]}",
                        execution_time=execution_time
                    )
                
                raise
        
        return wrapper
    return decorator


def with_search_tracking(search_type: str = "web"):
    """
    Specialized decorator for search functions.
    
    Automatically extracts search queries and results for knowledge graph.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract context and search request
            ctx = None
            search_request = None
            
            for arg in args:
                if hasattr(arg, 'deps') and hasattr(arg.deps, 'knowledge_graph'):
                    ctx = arg
                elif hasattr(arg, 'query'):  # Likely a SearchRequest
                    search_request = arg
            
            if not ctx:
                return await func(*args, **kwargs)
            
            # Execute original function
            result = await func(*args, **kwargs)
            
            # Track search in knowledge graph
            if search_request and result:
                # Get or create KG manager
                if not hasattr(ctx.deps, '_kg_manager'):
                    from .knowledge_graph import KnowledgeGraphManager
                    ctx.deps._kg_manager = KnowledgeGraphManager()
                
                kg_manager = ctx.deps._kg_manager
                
                await kg_manager.add_search(
                    query=search_request.query,
                    results=str(result),
                    search_type=search_type,
                    location=getattr(search_request, 'location', None)
                )
                
                logger.debug(f"🧠 KG tracked search: {search_request.query}")
            
            return result
        
        return wrapper
    return decorator


def with_entity_creation(entity_type: str, name_extractor: Optional[Callable[[Any], str]] = None):
    """
    Decorator for functions that create or discover entities.
    
    Args:
        entity_type: Type of entity being created
        name_extractor: Function to extract entity name from result
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            ctx = None
            for arg in args:
                if hasattr(arg, 'deps') and hasattr(arg.deps, 'knowledge_graph'):
                    ctx = arg
                    break
            
            result = await func(*args, **kwargs)
            
            if ctx and result:
                if not hasattr(ctx.deps, '_kg_manager'):
                    from .knowledge_graph import KnowledgeGraphManager
                    ctx.deps._kg_manager = KnowledgeGraphManager()
                
                kg_manager = ctx.deps._kg_manager
                
                # Extract entity name
                if name_extractor:
                    entity_name = name_extractor(result)
                else:
                    entity_name = str(result)[:50]  # Default: truncate result
                
                await kg_manager.add_entity(
                    name=entity_name,
                    entity_type=entity_type,
                    properties={
                        "created_by": func.__name__,
                        "result_preview": str(result)[:100]
                    }
                )
                
                logger.debug(f"🧠 KG created entity: {entity_name} ({entity_type})")
            
            return result
        
        return wrapper
    return decorator


# Convenience functions for common patterns
def track_search(search_type: str = "web"):
    """Shorthand for search tracking"""
    return with_search_tracking(search_type)


def track_function(entity_type: str = "function_call"):
    """Shorthand for basic function tracking"""
    return with_knowledge_graph(entity_type)


def track_entity(entity_type: str, name_from_result: bool = True):
    """Shorthand for entity creation tracking"""
    extractor = (lambda x: str(x)[:50]) if name_from_result else None
    return with_entity_creation(entity_type, extractor)